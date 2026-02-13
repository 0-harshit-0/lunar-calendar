import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/controls/OrbitControls.js';

import { EffectComposer } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/postprocessing/ShaderPass.js';



const spaceCanvas = document.querySelector('#spaceCanvas');
let renderAnimationID = null;

const BLOOM_LAYER = 1;
const PLANET_POS_SCALE = 5e-7; //1e-6; //1e-7;
const PLANET_RADIUS_SCALE = 3e-4;

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
  ["Mercury", 0xbdbdbd], // bright warm gray
  ["Venus",   0xffd54f], // golden yellow
  ["Earth",   0x2196f3], // vivid blue
  ["Mars",    0xff5722], // bright red-orange
  ["Jupiter", 0xffcc80], // warm orange-beige
  ["Saturn",  0xffe082], // pale gold
  ["Uranus",  0x4dd0e1], // bright cyan
  ["Neptune", 0x2962ff]  // electric deep blue
]);




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


// THREE.Object3D.DefaultUp = new THREE.Vector3(0, 0, 1);
const scene = new THREE.Scene();
// const light = new THREE.DirectionalLight('white', 1);
// const ambientLight = new THREE.AmbientLight('white', 1);
const camera = new THREE.PerspectiveCamera(
  100, // fov
  window.innerWidth / window.innerHeight, // aspect
  10, // near
  3000 // far
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


// camera.up.set(0, 0, 1);
camera.position.set(0, 0, 100);
// camera.lookAt(0, 300, 0);

renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = false;
// renderer.shadowMap.type = THREE.PCFSoftShadowMap; // Softer shadows
renderer.physicallyCorrectLights = false;

bloomComposer.setSize(window.innerWidth, window.innerHeight);
finalComposer.setSize(window.innerWidth, window.innerHeight);


// document.body.appendChild(renderer.domElement);

controls.target.set(0, 0, 0);


// Planets Class

class Planet {
	constructor(id, name, x, y, z, r, c, distInfo) {
		this.id = id;
		this.name = name;

		// const dir = new THREE.Vector3(x, y, z);
		// const realDist = dir.length();
		// console.log(realDist, dir, "dir")

		// dir.normalize();
		// const scaledDist = this.remapDistance(
		// 	realDist,
		// 	distInfo.min,
		// 	distInfo.max
		// );

		// this.pos = dir.multiplyScalar(scaledDist);

		this.pos = new THREE.Vector3(x, y, z);
		this.pos.multiplyScalar(PLANET_POS_SCALE);
		this.radius = Math.min((r * PLANET_RADIUS_SCALE) > 20 ? (r * PLANET_RADIUS_SCALE)/2 : r * PLANET_RADIUS_SCALE, 20);
		this.color = c;
	}
	draw() {
		this.geometry = new THREE.SphereGeometry( this.radius, 64, 64 );
		this.material = new THREE.MeshBasicMaterial({
			color: this.color ?? 0xffff00,
			// roughness: 1.0,
			// metalness: 0.0
		});

		this.mesh = new THREE.Mesh( this.geometry, this.material );
		this.mesh.position.copy(this.pos);

		return this.mesh;
	}
	remapDistance(d, min, max, outMin = 100, outMax = 1500) {
		const logMin = Math.log(min);
		const logMax = Math.log(max);
		const logD = Math.log(d);

		const t = (logD - logMin) / (logMax - logMin);
		return outMin + t * (outMax - outMin);
	}
	info() {
		return this;
	}
}

class Sun extends Planet {
	constructor(id, name, x,y,z, r, c, distInfo) {
		super(id, name, x,y,z, r, c, distInfo);

		this.pos = new THREE.Vector3(0,0,0);
		// console.log(r * PLANET_RADIUS_SCALE)
		this.radius = 15; //Math.min((r * PLANET_RADIUS_SCALE) > 20 ? (r * PLANET_RADIUS_SCALE)/2 : r * PLANET_RADIUS_SCALE, 20);
	}
	draw() {
		super.draw();

		// this.mesh.material.emissive = new THREE.Color(this.color);
		// this.mesh.material.emissiveIntensity = 1;
		this.mesh.layers.enable(BLOOM_LAYER);

		// this.light = new THREE.PointLight(0xffffff, 300000);
		// this.light.castShadow = true;
		// this.mesh.add(this.light);

		return this.mesh;
	}
	static computeDistanceStats(planets) {
		let min = Infinity;
		let max = 0;

		planets.forEach(p => {
			if (p.name === "Sun") return;

			const d = new THREE.Vector3(...p.xyz).length();
			p._dist = d;

			min = Math.min(min, d);
			max = Math.max(max, d);
		});

		return { min, max };
	}
}


// draw all

const planetsMesh = [];

function planetsDraw(data) {
	if (!data) return 0;

	const distInfo = Sun.computeDistanceStats(data.planets);

	data.planets.forEach((z, i) => {
		if (!PlanetRadiiKM.get(z.name)) return;

		let planet;

		if (z.name == "Sun") {
			planet = new Sun(i, z.name, ...z.xyz, PlanetRadiiKM.get(z.name), new THREE.Color(PlanetColors.get(z.name)), { min: 0, max: 0 });
		}else {
			planet = new Planet(
				i,
				z.name,
				...z.xyz,
				PlanetRadiiKM.get(z.name),
				new THREE.Color(PlanetColors.get(z.name)),
				distInfo
			);
		}

			console.log(planet.pos, planet.name)
		planetsMesh.push(planet.draw());
	});
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

function onResize() {
  const width = window.innerWidth;
  const height = window.innerHeight;

  camera.aspect = width / height;
  camera.updateProjectionMatrix();

  renderer.setSize(width, height);
  bloomComposer.setSize(width, height);
  finalComposer.setSize(width, height);
}



// lights, camera, controls setup ======================
	// console.log(data, planetsMesh)

	// scene.add(ambientLight);
	// scene.add(light);
	// scene.add(light.target);
export function init(data) {
  if (!data) return 0;

  planetsMesh.forEach(mesh => scene.remove(mesh));
  planetsMesh.length = 0;

  planetsDraw(data);
  planetsMesh.forEach(z => scene.add(z));

	scene.add(camera);
  controls.update();

  animate();
}


window.addEventListener('resize', onResize);

renderer.domElement.addEventListener('webglcontextlost', (e) => {
  e.preventDefault();
  console.log('WebGL context lost');
});

renderer.domElement.addEventListener('webglcontextrestored', () => {
  console.log('WebGL context restored');
});
