/*
*Tree builder from xyz coords in .csv
*This is setup to use the Blender Zarr scripts to output an elevation corrected treelist.
*/

AFRAME.registerComponent('tree-builder', {
	schema: {
		innerHeight: { type: 'number', default: 500.0 },//don't modify, used internally.
	    innerWidth: { type: 'number', default: 500.0 },//don't modify, used internally.
	    species: { type: 'array', default: [] }
	},

	init: function () {
	    var el = this.el;
	    var data = this.data;
	
	    var sheet = document.querySelector( '#treesheet' );
	    var treecoords = sheet.data;
	    var rows = [];
	    rows = treecoords.split(/\n/);
	
	    var treeLocs = [];
	    var treeHeights = [];

	    /*TREELIST CSV COLUMNS
	    ,SPCD,DIA_cm,HT_m,STATUSCD,CBH_m,CROWN_RADIUS_m,X_m,Y_m,Z_m,basal_tree_ft^2
	    //Skip the first row as headers in the following loop.
	    //May need to adjust x,y,z index for position due to variance between programs
	    //rows.length -1 because .csv contains a blank last row.
	    */
	    for (var i = 1; i < rows.length - 1; i++) {
	      rowArray = rows[i].split(",");
	      //NOTE for future: outMin + ( float( num - inMin ) / float(inMax - inMin ) * ( outMax - outMin ) )
	      treeLocs.push( rowArray[ 8 ] );//z
	      treeLocs.push( rowArray[ 9 ] );//y is up in THREE but z is up in Blender
	      treeLocs.push( rowArray[ 7 ] );//x
	      treeHeights.push( rowArray[ 3 ] );
	      //push uv value to shader for image selection from an atlas image 
	      if( rowArray[ 1 ] == 122 || rowArray[ 1 ] == 116 || rowArray[ 1 ] == 117 ){
	        data.species.push( 0.0, 0.0 );
	      } else if( rowArray[ 1 ] == 202 ){
	        data.species.push( 0.33, 0.0 );
	      } else if( rowArray[ 1 ] == 15  ){
	        data.species.push( 0.0, 0.5 );
	      } else if( rowArray[ 1 ] == 801 || rowArray[ 1 ] == 839 ) {
	        data.species.push( 2.0 / 3.0, 1.0 / 2.0 );
	      } else if ( rowArray[ 1 ] == 763 ) {
	        data.species.push( 0.33, 0.5 );
	      } else {
	        data.species.push( 0.0, 0.0 );
	      }
	    };

	    var treepoints = new THREE.BufferGeometry();
	    treepoints.setAttribute('position', new THREE.Float32BufferAttribute( treeLocs, 3 ) );
	    treepoints.setAttribute( 'size', new THREE.Float32BufferAttribute( treeHeights, 1 ) );
	    treepoints.setAttribute( 'species', new THREE.Float32BufferAttribute( data.species, 2 ) );
	    treepoints.computeBoundingBox();

    	//console.log( data. species );
    	//CREATE CUSTOM MATERIAL

    	var textureLoader = new THREE.TextureLoader();

	    uniforms = {
	      "treeAtlas": { value: textureLoader.load( './images/treeTextureAtlas.png', ( texture ) => { texture.flipY = false; } ) },
	      "screenheight": { value: data.innerHeight },
	      "screenwidth": { value: data.innerWidth }
		};

	    this.custom_material = new THREE.ShaderMaterial({
	
	      uniforms: uniforms,
				
	      vertexShader: `
	      
	        attribute float size;
	        attribute vec2 species;
	        uniform float screenheight;
	        uniform float screenwidth;
	        uniform vec4 origin;
	
	        out vec2 speciesAtlasCoord;
	
	        void main()
	        {
	
	            vec4 mvPosition = modelViewMatrix * vec4( position.x, position.y + size / 2.0, position.z, 1.0 );
	            
	            float camDist = distance( mvPosition, origin );
	            float aspectRatio = screenwidth / screenheight;
	            
	            gl_PointSize = size * screenheight / ( camDist * aspectRatio ); 
	            gl_Position = projectionMatrix * mvPosition;
	
	            speciesAtlasCoord = species;
	        }
	        `
	      ,
	      fragmentShader: `
	
	        precision mediump float;
	
	        uniform vec3 color;
	        uniform sampler2D treeAtlas;
	        in vec2 speciesAtlasCoord;
	
		void main( void ) {
	
	          float columns = 3.0;
	          float rows = 2.0;
	          
	          vec2 uvOffset = speciesAtlasCoord;
	          vec2 uvScale = vec2( 1.0 / columns, 1.0 / rows );
	          
	          vec2 atUV = ( gl_PointCoord * uvScale ) + uvOffset;
	
	          vec4 color = texture2D( treeAtlas, atUV );
	
	          gl_FragColor = color;
		}
		`
	      ,
	      //Adds the transparency value to the Three.js material so the dot looks
	      //like a dot and not the square texture it is.
	      transparent: true,
	      depthTest: true,
	      depthWrite: false
	
	      });

	    //var treePointDisplay = new THREE.Points( treepoints, treePointMaterial );
	    var treePointDisplay = new THREE.Points( treepoints, this.custom_material );
	
	    el.setObject3D( 'mesh', treePointDisplay );
	    
	    el.setAttribute( 'rotation', '0 0 0' );

	    //Handle window resizing by updating data
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
    	this.custom_material.uniforms.screenheight.value = data.innerHeight;
    	this.custom_material.uniforms.screenwidth.value = data.innerWidth;
	}

});
