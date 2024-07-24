/*
This component requires
    *A FastFuels z-enabled treelist.csv
    *Tree images by species to texture points with
Creates Three.js points geometries for each species, and assigns a custom whole tree image as the texture
If no image exists, assigns random color point all trees of a species.
Scales the point size to the height of the tree (HT_m).
Each species is included in an AFrame SPCD entity.
    *This allows for potential of toggling visibility on all Ponderose Pine at once, for example.
        *var treegroup = document.querySelector( '#122' );
        *treegroup.setAttribute( 'visibility', false );
The getImagePath() function demonstrates a possible way to incorporate a tree database of paths.
*/

AFRAME.registerComponent('tree-builder', {
	schema: {
    treelist: { type: 'string', default: '' },
    innerHeight: { type: 'number', default: 500.0 },//don't modify, used internally.
    innerWidth: { type: 'number', default: 500.0 },//don't modify, used internally.
    materials: { type: 'array', default: [] }//don't modify, used internally.
    },

	init: function () {
        var el = this.el;
        var data = this.data;

        this.allSpeciesList = [];
        this.uniqueSpeciesList = [];
        this.speciesShaderList = [];

        this.textureLoader = new THREE.TextureLoader();

        if( data.treelist === '' ) {
            console.log( 'No treelist is specified in html <a-assets>.' );
        } else {
            this.readTreeList();
        }

        //Handle window resizing by updating data in schema
        window.addEventListener('resize', () => {
            data.innerHeight = window.innerHeight;
            data.innerWidth = window.innerWidth;
        });

    },
    
    update: function () {},

	remove: function () {},

	play: function () {},

	pause: function () {},

    tick: function (t, dt) {
        //Use the tick function to constantly check for new window sizing in data.
        var data = this.data;
        for( var m = 0; m < data.materials.length; m++ ) {
            data.materials[ m ].uniforms.screenheight.value = data.innerHeight;
            data.materials[ m ].uniforms.screenwidth.value = data.innerWidth;
        }
    },

    createPointsGeometry: function ( speciescode ) {
        //Create Points Geometry and Material for each species.
        var el = this.el;
        var data = this.data;
        var locs = [];
        var heights = [];
        var perSpeciesPointsGeom = new THREE.BufferGeometry();

        //read csv and create buffergeom from data for the species
        //start at index 1 due to headers and skip last row due to NaN/blanks in csv
        var treeList = document.querySelector( data.treelist );
        treedata = treeList.data;
        var rows = [];
        rows = treedata.split( /\n/ );
        
        for( s = 1; s < rows.length - 1; s++  ){
            rowArray = rows[ s ].split( "," );
            if( rowArray[ 1 ] === speciescode ) {
                //Remember the data has y before x so z before x here
                locs.push( rowArray[ 8 ] );//z
                locs.push( rowArray[ 9 ] );//y is up in THREE but z is up in Blender
                locs.push( rowArray[ 7 ] );//x
                heights.push( rowArray[ 3 ] );
            }
        }

        //Location of tree
        perSpeciesPointsGeom.setAttribute( 'position', new THREE.Float32BufferAttribute( locs, 3 ) );
        //Height of tree
        perSpeciesPointsGeom.setAttribute( 'size', new THREE.Float32BufferAttribute( heights, 1 ) );

        /*
        Create glsl material per species with specific whole tree image.
        If no whole tree image exists in list, use random colored point for now.
        */
        var imagepath = this.getImagePath( speciescode );
        
        if( imagepath ) {
            uniforms = {
                "treeImage": { value: this.textureLoader.load( imagepath, ( texture ) => { texture.flipY = false; } ) },
                "screenheight": { value: data.innerHeight },
                "screenwidth": { value: data.innerWidth }
            };
    
            var perSpeciesMaterial = new THREE.ShaderMaterial( {
                
                uniforms: uniforms,

                vertexShader: `
                    attribute float size;
                    uniform float screenheight;
                    uniform float screenwidth;
                    uniform vec4 origin;
        
                    void main()
                    {
                        vec4 mvPosition = modelViewMatrix * vec4( position.x, position.y + ( size / 2.0 ), position.z, 1.0 );
                        
                        float camDist = distance( mvPosition, origin );
                        float aspectRatio = screenwidth / screenheight;
                        
                        gl_PointSize = size * screenheight / ( camDist * aspectRatio );
                        //gl_PointSize = size;
                        gl_Position = projectionMatrix * mvPosition;
                    }
                `,

                fragmentShader: `
                    uniform vec3 color;
                    uniform sampler2D treeImage;

                    void main( void ) {
                
                        //test for seasonal color.
                        vec4 seasonColor = vec4( 1.0, 1.0, 1.0, 0.8 );

                        vec4 color = texture2D( treeImage, gl_PointCoord );

                        //gl_FragColor = color;
                        gl_FragColor = color * seasonColor;
                    }
                `
                ,
                transparent: true,
                depthTest: true,
                depthWrite: false,
                forceSinglePass: true
            });
            
            //add materials to component data array so we can loop it in tick
            data.materials.push( perSpeciesMaterial );

        } else{
            var ranColor = new THREE.Color( Math.random(), Math.random(), Math.random() );
            var perSpeciesMaterial = new THREE.PointsMaterial( { color: ranColor, size: 3.0  } );
        }
        
        var material = perSpeciesMaterial;

        var speciesPointDisplay = new THREE.Points( perSpeciesPointsGeom, material );
        this.addToScene( speciescode, speciesPointDisplay );
    },

    addToScene: function ( species, speciesGeom ) {
        //Adds the geometry to the scene as a sub-entity with species ID
        var el = this.el;
        var speciesEntity = document.createElement( 'a-entity' );

        speciesEntity.setAttribute( 'id', species );
        speciesEntity.setObject3D( 'mesh', speciesGeom );
        el.appendChild( speciesEntity );
    },

    readTreeList: function () {
        //read csv and set initial arrays for species to loop through.
        var data = this.data;
        var treeList = document.querySelector( data.treelist );
        treedata = treeList.data;
        var rows = [];
        rows = treedata.split( /\n/ );

        for ( var a = 1; a < rows.length - 1; a++ ) {
            rowArray = rows[ a ].split(",");
            this.allSpeciesList.push( rowArray[ 1 ] );
        }

        //Create array of unique species in data
        this.uniqueSpeciesList = this.allSpeciesList.filter( ( value, index, array ) => array.indexOf( value ) === index );

        //Send each species to create a geometry
        for( var b = 0; b < this.uniqueSpeciesList.length; b++ ) {
            this.createPointsGeometry( this.uniqueSpeciesList[ b ] );
        }

    },

    getImagePath: function( speciescode ) {
        //Contains the species list and image path as an array and returns the path of image for a given species if available.
        var speciesTable = [
            //SPCD, path to image, path to spcd texture atlas?. . . .
            [ 15, './images/15_WhiteFir_Whole_1024x1024.png', ''  ],
            [ 81, './images/81_IncenseCedar_1024x1024.png', '' ],
            [ 108, './images/108_LodgePolePine_512x512.png', '' ],
            [ 122, './images/122_PonderosaPine_Whole_512x512.png', '' ],
            [ 202, './images/202_DouglasFir_Whole_512x512.png', ''  ],
            [ 763, './images/763_Chokecherry_Whole_1024x1024.png', '' ],
            [ 746, './images/746_QuakingAspen_512x512.png', '' ],
            [ 839, './images/839_InteriorLiveOak_Whole_1024x1024.png', '' ]
        ];

        for( i = 0; i < speciesTable.length; i++ ) {
            if( parseInt( speciesTable[ i ][ 0 ] ) === parseInt( speciescode ) ){
                return  speciesTable[ i ][ 1 ];
            }
        }
    }

});

