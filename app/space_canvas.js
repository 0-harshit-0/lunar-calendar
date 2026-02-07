import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/controls/OrbitControls.js';

import { EffectComposer } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/postprocessing/ShaderPass.js';




const BLOOM_LAYER = 1;
const PLANET_POS_SCALE = 5e-7; //1e-6; //1e-7;
const PLANET_RADIUS_SCALE = 5e-4;

// Planetary mean radii in kilometers
const PlanetRadiiKM = new Map([
	["Sun", 696340],
	["Mercury", 2439.7],
  	["Venus", 6051.8],
	["Earth", 6371.0],
  	["Mars", 3389.5],
  	["Jupiter", 69911],
  	["Saturn", 58232],
  	["Uranus", 25362],
  	["Neptune", 24622]
]);
const PlanetColors = new Map([
  ["Sun", 0xffffff],      // 0xffcc33 yellow-orange
  ["Mercury", 0x8c8c8c],  // dark gray
  ["Venus", 0xe6c27a],    // pale yellow
  ["Earth", 0x2a6bd4],    // blue
  ["Mars", 0xb5533c],    // red-orange
  ["Jupiter", 0xd2b48c], // tan
  ["Saturn", 0xf5deb3],  // light beige
  ["Uranus", 0x7fffd4],  // cyan
  ["Neptune", 0x4169e1]  // deep blue
]);


let renderAnimationID = null;


export function openSpace() {
  	spaceCanvas.style.display = "block";
}

export function closeSpace() {
	if (renderAnimationID) {
		cancelAnimationFrame(renderAnimationID);
	}
	spaceCanvas.style.display = "none";
	return 0;
}




// spaceCanvas
const spaceCanvas = document.querySelector('#spaceCanvas');
spaceCanvas.width = innerWidth;
spaceCanvas.height = innerHeight;


// THREE.Object3D.DefaultUp = new THREE.Vector3(0, 0, 1);
const scene = new THREE.Scene();
// const light = new THREE.DirectionalLight('white', 1);
const ambientLight = new THREE.AmbientLight(0x404040, 0.1);
const camera = new THREE.PerspectiveCamera(
  300, // fov
  window.innerWidth / window.innerHeight, // aspect
  100, // near
  6000 // far
);
const renderer = new THREE.WebGLRenderer({ canvas: spaceCanvas, antialias: true });
const controls = new OrbitControls(camera, spaceCanvas);
const bloomComposer = new EffectComposer(renderer);
bloomComposer.renderToScreen = false;
bloomComposer.addPass(new RenderPass(scene, camera));

const bloomPass = new UnrealBloomPass(
	new THREE.Vector2(window.innerWidth, window.innerHeight),
	1.5,
	0.4,
	0.85
);

bloomComposer.addPass(bloomPass);

const finalComposer = new EffectComposer(renderer);
finalComposer.addPass(new RenderPass(scene, camera));
finalComposer.addPass(
	new ShaderPass(
		new THREE.ShaderMaterial({
			uniforms: {
				baseTexture: { value: null },
				bloomTexture: { value: bloomComposer.renderTarget2.texture }
			},
			vertexShader: `
				varying vec2 vUv;
				void main() {
					vUv = uv;
					gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
				}
			`,
			fragmentShader: `
				uniform sampler2D baseTexture;
				uniform sampler2D bloomTexture;
				varying vec2 vUv;
				void main() {
					vec4 base = texture2D(baseTexture, vUv);
					vec4 bloom = texture2D(bloomTexture, vUv);
					gl_FragColor = base + bloom;
				}
			`
		}),
		'baseTexture'
	)
);
bloomPass.strength = 0.6;
bloomPass.radius = 0.25;
bloomPass.threshold = 0.9;


scene.background = new THREE.Color('black');

// light.position.set(0, 30, 100);
// light.target.position.set(0, 2, 0);
// light.castShadow = true;
// // if bigger size
// light.shadow.mapSize.width = 2048;
// light.shadow.mapSize.height = 2048;

// light.shadow.camera.near = 1;
// light.shadow.camera.far = 500;

// light.shadow.camera.left = -100;
// light.shadow.camera.right = 100;
// light.shadow.camera.top = 100;
// light.shadow.camera.bottom = -100;

// camera.up.set(0, 0, 1);
camera.position.set(0, 0, 100);
// camera.lookAt(0, 300, 0);

renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap; // Softer shadows
renderer.physicallyCorrectLights = false;

// document.body.appendChild(renderer.domElement);

controls.target.set(0, 0, 0);


// Planets Class

class Planet {
	constructor(id, name, x, y, z, r, c) {
		this.id = id;
		this.name = name;

		this.pos = new THREE.Vector3(x, y, z);
		this.radius = name == "Sun" ? 20 : r * PLANET_RADIUS_SCALE; //Math.min((r * PLANET_RADIUS_SCALE) > 20 ? (r * PLANET_RADIUS_SCALE)/2 : r * PLANET_RADIUS_SCALE, 20);
		this.color = c;

		this.geometry = new THREE.SphereGeometry( this.radius, 64, 64 );
		this.material = new THREE.MeshStandardMaterial( {
			color: this.color ?? 0xffff00,
			// roughness: 1.0,
			// metalness: 0.0
		} );
		this.mesh = new THREE.Mesh( this.geometry, this.material );

		this.pos.multiplyScalar(PLANET_POS_SCALE);
		this.mesh.position.copy(this.pos);
	}
	draw() {
		return this.mesh;
	}
	info() {
		return this;
	}
}

class Sun extends Planet {
	constructor(id, name, x,y,z, r, c) {
		super(id, name, x,y,z, r, c);

		this.mesh.material.emissive = new THREE.Color(c);
		this.mesh.material.emissiveIntensity = 1;

		this.light = new THREE.PointLight(0xffffff, 300000, 0);
		this.light.castShadow = true;
		this.mesh.add(this.light);
		this.mesh.layers.enable(BLOOM_LAYER);
	}
}


// draw all

const planetsMesh = [];

function planetsDraw(data) {
	if (!data) return 0;

	data.planets.forEach((z, i) => {
		if(PlanetRadiiKM.get(z.name)) {
			let planet;
			if (z.name == "Sun") {
				planet = new Sun(i, z.name, ...z.xyz, PlanetRadiiKM.get(z.name), new THREE.Color(PlanetColors.get(z.name)));
			}else {
				planet = new Planet(i, z.name, ...z.xyz, PlanetRadiiKM.get(z.name), new THREE.Color(PlanetColors.get(z.name)));
			}
			console.log(planet.pos, planet.name)
			planetsMesh.push(planet.draw());
		}
	})

}



function renderFun() {
  // console.log('r');
  // renderer.render(scene, camera);
 	camera.layers.set(BLOOM_LAYER);
	bloomComposer.render();

	camera.layers.set(0);
	finalComposer.render();
}


function animate() {
	renderFun();

	renderAnimationID = requestAnimationFrame(animate);
}


// lights, camera, controls setup ======================
export function init(data) {
	if (!data) return 0;
	planetsDraw(data);
	console.log(data, planetsMesh)

	scene.add(ambientLight);
	// scene.add(light);
	// scene.add(light.target);
	scene.add(camera);
	planetsMesh.forEach(z => scene.add(z));
	controls.update();

	animate();
}