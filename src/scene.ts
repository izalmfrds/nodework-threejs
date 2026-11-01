import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { loadOffice } from './office';
import { whenScrollIdle } from './scroll-idle';

type ProjectKind = 'operations' | 'dashboard' | 'location';
type Motion = (seconds: number) => void;

const C = {
  white: 0xf2f7ff,
  ice: 0xc6d9f8,
  frost: 0x93b6ec,
  silver: 0x658fd4,
  cobalt: 0x0648f5,
  electric: 0x2679ff,
  cyan: 0x65d6ff,
  navy: 0x091d55,
  deep: 0x102b69,
};

const matte = (color: number, roughness = 0.57, metalness = 0.1) =>
  new THREE.MeshStandardMaterial({ color, roughness, metalness });
const glow = (color: number, intensity = 0.7) =>
  new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: intensity, roughness: 0.3, metalness: 0.12 });

const white = matte(C.white);
const ice = matte(C.ice);
const frost = matte(C.frost);
const silver = matte(C.silver, 0.38, 0.44);
const cobalt = matte(C.cobalt, 0.35, 0.18);
const electric = glow(C.electric, 0.45);
const cyan = glow(C.cyan, 0.75);
const navy = matte(C.navy, 0.4, 0.25);
const deep = matte(C.deep, 0.34, 0.25);

function block(
  parent: THREE.Object3D,
  dimensions: [number, number, number],
  position: [number, number, number],
  material: THREE.Material,
  radius = 0.055,
) {
  const [width, height, depth] = dimensions;
  const geometry = new RoundedBoxGeometry(width, height, depth, 3, Math.min(radius, width / 3, height / 3, depth / 3));
  const mesh = new THREE.Mesh(geometry, material);
  mesh.position.set(...position);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  parent.add(mesh);
  return mesh;
}

function cylinder(
  parent: THREE.Object3D,
  radius: number,
  height: number,
  position: [number, number, number],
  material: THREE.Material,
  sides = 18,
) {
  const mesh = new THREE.Mesh(new THREE.CylinderGeometry(radius, radius, height, sides), material);
  mesh.position.set(...position);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  parent.add(mesh);
  return mesh;
}

function sphere(
  parent: THREE.Object3D,
  radius: number,
  position: [number, number, number],
  material: THREE.Material,
) {
  const mesh = new THREE.Mesh(new THREE.SphereGeometry(radius, 16, 12), material);
  mesh.position.set(...position);
  mesh.castShadow = true;
  parent.add(mesh);
  return mesh;
}

function tube(parent: THREE.Object3D, points: THREE.Vector3[], radius: number, material: THREE.Material) {
  const curve = new THREE.CatmullRomCurve3(points);
  const mesh = new THREE.Mesh(new THREE.TubeGeometry(curve, Math.max(14, points.length * 7), radius, 8, false), material);
  mesh.castShadow = true;
  parent.add(mesh);
  return mesh;
}

function lineBetween(parent: THREE.Object3D, start: THREE.Vector3, end: THREE.Vector3, radius: number, material: THREE.Material) {
  const direction = end.clone().sub(start);
  const mesh = new THREE.Mesh(new THREE.CylinderGeometry(radius, radius, direction.length(), 10), material);
  mesh.position.copy(start).add(end).multiplyScalar(0.5);
  mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), direction.normalize());
  mesh.castShadow = true;
  parent.add(mesh);
  return mesh;
}

function makeCanvasTexture(draw: (ctx: CanvasRenderingContext2D, width: number, height: number) => void, width = 512, height = 320) {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d')!;
  draw(ctx, width, height);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = 4;
  return texture;
}

function factoryPanelTexture(label: string, index: number) {
  return makeCanvasTexture((ctx, width, height) => {
    const gradient = ctx.createLinearGradient(0, 0, width, height);
    gradient.addColorStop(0, '#1459f3');
    gradient.addColorStop(1, '#62b4fa');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);
    ctx.strokeStyle = 'rgba(255,255,255,.66)';
    ctx.lineWidth = 4;
    ctx.strokeRect(17, 17, width - 34, height - 34);
    ctx.font = '700 58px Arial, sans-serif';
    ctx.fillStyle = '#fff';
    ctx.fillText(label, 38, 87);
    ctx.strokeStyle = 'rgba(255,255,255,.83)';
    ctx.lineWidth = 5;
    if (index === 0) {
      ctx.strokeRect(45, 126, 132, 124);
      ctx.strokeRect(72, 145, 132, 124);
      ctx.beginPath(); ctx.moveTo(45, 126); ctx.lineTo(72, 145); ctx.moveTo(177, 126); ctx.lineTo(204, 145); ctx.stroke();
    } else if (index === 4) {
      for (let i = 0; i < 4; i++) ctx.fillRect(54 + i * 39, 244 - i * 29, 24, 34 + i * 29);
    } else {
      ctx.strokeRect(48, 130, 180, 124);
      ctx.beginPath();
      ctx.moveTo(83, 174); ctx.lineTo(105, 191); ctx.lineTo(83, 208);
      ctx.moveTo(189, 174); ctx.lineTo(168, 191); ctx.lineTo(189, 208);
      ctx.stroke();
    }
    ctx.lineWidth = 3;
    for (let i = 0; i < 4; i++) {
      ctx.beginPath(); ctx.moveTo(290, 151 + i * 32); ctx.lineTo(442 - i * 20, 151 + i * 32); ctx.stroke();
    }
  });
}

function processorTexture() {
  return makeCanvasTexture((ctx, width, height) => {
    const gradient = ctx.createLinearGradient(0, 0, width, height);
    gradient.addColorStop(0, '#1041cf');
    gradient.addColorStop(1, '#247cff');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);
    ctx.strokeStyle = '#d8f3ff';
    ctx.lineWidth = 8;
    ctx.strokeRect(31, 31, width - 62, height - 62);
    ctx.strokeRect(126, 94, 250, 130);
    ctx.beginPath();
    ctx.moveTo(122, 160); ctx.lineTo(82, 160); ctx.lineTo(82, 258); ctx.lineTo(208, 258);
    ctx.moveTo(378, 160); ctx.lineTo(424, 160); ctx.lineTo(424, 258); ctx.lineTo(303, 258);
    ctx.moveTo(251, 94); ctx.lineTo(251, 42);
    ctx.stroke();
    for (const [x, y] of [[82, 160], [208, 258], [424, 160], [303, 258], [251, 42]]) {
      ctx.fillStyle = '#f4fbff';
      ctx.beginPath(); ctx.arc(x, y, 12, 0, Math.PI * 2); ctx.fill();
    }
    ctx.font = 'bold 64px Arial, sans-serif';
    ctx.fillStyle = '#fff';
    ctx.textAlign = 'center';
    ctx.fillText('</>', 251, 178);
  });
}

function dashboardTexture(kind: ProjectKind) {
  return makeCanvasTexture((ctx, width, height) => {
    ctx.fillStyle = '#09183d';
    ctx.fillRect(0, 0, width, height);
    const gradient = ctx.createLinearGradient(0, 0, width, height);
    gradient.addColorStop(0, 'rgba(23,68,164,.88)');
    gradient.addColorStop(1, 'rgba(3,14,44,.05)');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);
    ctx.fillStyle = '#3e86ff';
    ctx.fillRect(0, 0, 36, height);
    for (let i = 0; i < 6; i++) {
      ctx.fillStyle = i === 1 ? '#88c9ff' : 'rgba(183,207,255,.35)';
      ctx.fillRect(10, 50 + i * 38, 14, 14);
    }
    ctx.font = 'bold 27px Arial, sans-serif';
    ctx.fillStyle = '#f7fbff';
    ctx.fillText(kind === 'operations' ? 'Operations' : kind === 'dashboard' ? 'Analytics' : 'Location intelligence', 59, 52);
    ctx.font = '17px Arial, sans-serif';
    ctx.fillStyle = '#8aa9ee';
    ctx.fillText('LIVE SYSTEM OVERVIEW', 59, 81);
    ctx.strokeStyle = 'rgba(114,164,255,.45)';
    ctx.lineWidth = 2;
    for (let i = 0; i < 3; i++) ctx.strokeRect(58 + i * 141, 110, 119, 72);
    ctx.fillStyle = '#e8f2ff';
    ctx.font = 'bold 30px Arial, sans-serif';
    ['24.8K', '98.4%', '7.2M'].forEach((value, i) => ctx.fillText(value, 70 + i * 141, 153));
    ctx.strokeStyle = '#418bff';
    ctx.lineWidth = 6;
    ctx.beginPath();
    const values = kind === 'location' ? [239, 225, 240, 206, 194, 218, 178, 190, 160, 153, 132, 138] : [249, 221, 235, 199, 216, 181, 164, 177, 140, 152, 118, 104];
    values.forEach((value, i) => i === 0 ? ctx.moveTo(60 + i * 39, value) : ctx.lineTo(60 + i * 39, value));
    ctx.stroke();
    ctx.fillStyle = 'rgba(55,143,255,.36)';
    for (let i = 0; i < 12; i++) ctx.fillRect(60 + i * 38, 284 - (i % 5) * 12, 21, 25 + (i % 5) * 12);
  }, 512, 320);
}

function phoneTexture(kind: 'dashboard' | 'location') {
  return makeCanvasTexture((ctx, width, height) => {
    ctx.fillStyle = '#07183c';
    ctx.fillRect(0, 0, width, height);
    const gradient = ctx.createLinearGradient(0, 0, width, height);
    gradient.addColorStop(0, '#183e8c');
    gradient.addColorStop(0.65, '#0b2256');
    gradient.addColorStop(1, '#061334');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);
    ctx.fillStyle = '#c9dcff';
    ctx.font = '16px Arial, sans-serif';
    ctx.fillText('9:41', 24, 28);
    ctx.font = 'bold 24px Arial, sans-serif';
    ctx.fillStyle = '#f5f9ff';
    ctx.fillText(kind === 'location' ? 'Locations' : 'Analytics', 25, 75);
    ctx.fillStyle = '#74adff';
    ctx.font = '15px Arial, sans-serif';
    ctx.fillText(kind === 'location' ? 'CONNECTED NETWORK' : 'OVERVIEW', 25, 104);
    if (kind === 'location') {
      ctx.fillStyle = '#132f6a';
      ctx.fillRect(20, 132, 280, 264);
      ctx.strokeStyle = 'rgba(125,177,255,.3)';
      ctx.lineWidth = 2;
      for (let x = 48; x < 300; x += 42) { ctx.beginPath(); ctx.moveTo(x, 132); ctx.lineTo(x, 396); ctx.stroke(); }
      for (let y = 156; y < 396; y += 41) { ctx.beginPath(); ctx.moveTo(20, y); ctx.lineTo(300, y); ctx.stroke(); }
      ctx.strokeStyle = '#5d9cff';
      ctx.lineWidth = 10;
      ctx.beginPath(); ctx.moveTo(36, 325); ctx.bezierCurveTo(105, 282, 100, 196, 170, 223); ctx.bezierCurveTo(225, 240, 237, 170, 290, 158); ctx.stroke();
      for (const [x, y] of [[105, 270], [170, 223], [251, 180]]) {
        ctx.fillStyle = '#60b8ff';
        ctx.beginPath(); ctx.arc(x, y, 12, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = '#fff';
        ctx.beginPath(); ctx.arc(x, y, 4, 0, Math.PI * 2); ctx.fill();
      }
      ctx.fillStyle = '#eaf2ff';
      ctx.font = 'bold 19px Arial, sans-serif';
      ctx.fillText('12 live sites', 24, 432);
      ctx.font = '15px Arial, sans-serif';
      ctx.fillStyle = '#9fbef3';
      ctx.fillText('All systems connected', 24, 459);
    } else {
      ctx.fillStyle = '#eaf2ff';
      ctx.font = 'bold 46px Arial, sans-serif';
      ctx.fillText('92.8K', 24, 173);
      ctx.fillStyle = '#8caeea';
      ctx.font = '15px Arial, sans-serif';
      ctx.fillText('TOTAL EVENTS', 25, 199);
      ctx.fillStyle = '#102e69';
      ctx.fillRect(20, 230, 280, 176);
      ctx.strokeStyle = '#62a4ff';
      ctx.lineWidth = 5;
      ctx.beginPath();
      const values = [370, 352, 361, 329, 342, 304, 319, 275, 281, 254];
      values.forEach((value, i) => i ? ctx.lineTo(34 + i * 28, value) : ctx.moveTo(34, value));
      ctx.stroke();
      ctx.fillStyle = '#dceaff';
      ctx.font = 'bold 20px Arial, sans-serif';
      ctx.fillText('System performance', 24, 445);
      ctx.fillStyle = '#6fc8ff';
      ctx.fillRect(24, 465, 220, 9);
    }
  }, 320, 512);
}

function logoTexture() {
  return makeCanvasTexture((ctx, width, height) => {
    ctx.fillStyle = '#0753ff';
    ctx.fillRect(0, 0, width, height);
    ctx.strokeStyle = 'rgba(255,255,255,.8)';
    ctx.lineWidth = 18;
    ctx.beginPath(); ctx.arc(width / 2, height / 2, 160, 0, Math.PI * 2); ctx.stroke();
    ctx.fillStyle = '#fff';
    ctx.font = '900 240px Arial, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('N', width / 2, height / 2 + 10);
  }, 512, 512);
}

function createPanel(parent: THREE.Object3D, camera: THREE.Camera, label: string, index: number, x: number, y: number, z: number, motions: Motion[]) {
  const group = new THREE.Group();
  group.position.set(x, y, z);
  group.lookAt(camera.position);
  parent.add(group);
  block(group, [1.65, 1.16, 0.09], [0, 0, 0], new THREE.MeshPhysicalMaterial({ color: 0x5c9ff3, transparent: true, opacity: 0.83, roughness: 0.16, metalness: 0.2, depthWrite: false }), 0.1);
  const face = new THREE.Mesh(new THREE.PlaneGeometry(1.53, 1.04), new THREE.MeshBasicMaterial({ map: factoryPanelTexture(label, index), transparent: true, opacity: 0.97, side: THREE.DoubleSide }));
  face.position.z = 0.056;
  group.add(face);
  block(group, [0.045, 0.38, 0.045], [0, -0.78, 0], silver, 0.014);
  motions.push(t => {
    group.position.y = y + Math.sin(t * 0.85 + index * 1.2) * 0.055;
    (face.material as THREE.MeshBasicMaterial).opacity = 0.94 + Math.sin(t * 1.45 + index) * 0.035;
  });
}

function createWorker(parent: THREE.Object3D, x: number, z: number, motions: Motion[], phase = 0) {
  const worker = new THREE.Group();
  worker.position.set(x, -0.6, z);
  parent.add(worker);
  cylinder(worker, 0.17, 0.43, [0, 0.58, 0], white);
  cylinder(worker, 0.14, 0.17, [0, 0.89, 0], cobalt);
  sphere(worker, 0.17, [0, 1.05, 0], ice);
  block(worker, [0.39, 0.12, 0.17], [0, 1.17, 0], cobalt, 0.05);
  for (const side of [-1, 1]) {
    const leg = cylinder(worker, 0.065, 0.36, [side * 0.09, 0.18, 0], navy, 9);
    leg.rotation.z = side * 0.08;
    block(worker, [0.16, 0.08, 0.22], [side * 0.09, 0.035, 0.075], deep);
  }
  const leftArm = new THREE.Group();
  leftArm.position.set(-0.21, 0.75, 0);
  worker.add(leftArm);
  const rightArm = new THREE.Group();
  rightArm.position.set(0.21, 0.75, 0);
  worker.add(rightArm);
  cylinder(leftArm, 0.052, 0.36, [-0.03, -0.16, 0], white, 9).rotation.z = -0.25;
  cylinder(rightArm, 0.052, 0.36, [0.03, -0.16, 0], white, 9).rotation.z = 0.25;
  motions.push(t => {
    leftArm.rotation.x = Math.sin(t * 2.2 + phase) * 0.32 - 0.4;
    rightArm.rotation.x = Math.sin(t * 2.2 + phase + Math.PI) * 0.3 - 0.45;
    worker.position.y = -0.6 + Math.sin(t * 2.2 + phase) * 0.016;
  });
  return worker;
}

function createRobotArm(parent: THREE.Object3D, x: number, z: number, motions: Motion[]) {
  const base = new THREE.Group();
  base.position.set(x, -0.6, z);
  parent.add(base);
  cylinder(base, 0.41, 0.2, [0, 0.1, 0], navy);
  cylinder(base, 0.29, 0.2, [0, 0.29, 0], cobalt);
  const shoulder = new THREE.Group();
  shoulder.position.y = 0.36;
  base.add(shoulder);
  block(shoulder, [0.34, 1.65, 0.39], [0, 0.83, 0], white, 0.15);
  block(shoulder, [0.19, 1.2, 0.4], [0.2, 0.84, 0], ice, 0.08);
  const elbow = new THREE.Group();
  elbow.position.set(0, 1.64, 0);
  shoulder.add(elbow);
  sphere(elbow, 0.28, [0, 0, 0], cobalt);
  block(elbow, [0.39, 1.45, 0.37], [0, 0.72, 0], white, 0.13);
  block(elbow, [0.14, 1.05, 0.39], [0.19, 0.71, 0], frost, 0.05);
  const claw = new THREE.Group();
  claw.position.y = 1.43;
  elbow.add(claw);
  cylinder(claw, 0.24, 0.26, [0, 0.12, 0], cobalt);
  block(claw, [0.1, 0.38, 0.13], [-0.17, 0.38, 0], silver);
  block(claw, [0.1, 0.38, 0.13], [0.17, 0.38, 0], silver);
  motions.push(t => {
    base.rotation.y = Math.sin(t * 0.67) * 0.48;
    shoulder.rotation.z = -0.42 + Math.sin(t * 0.87) * 0.22;
    elbow.rotation.z = 0.93 + Math.sin(t * 0.87 + 1.1) * 0.25;
    claw.rotation.y = Math.sin(t * 1.4) * 0.22;
  });
}

function createConveyor(parent: THREE.Object3D, x: number, z: number, length: number, motions: Motion[], phase = 0) {
  block(parent, [length, 0.16, 1.03], [x, -0.43, z], ice, 0.06);
  block(parent, [length - 0.2, 0.065, 0.72], [x, -0.32, z], navy, 0.02);
  for (const edge of [-0.45, 0.45]) block(parent, [length, 0.19, 0.08], [x, -0.25, z + edge], silver, 0.025);
  const rollers: THREE.Mesh[] = [];
  const rollerGeometry = new THREE.CylinderGeometry(0.065, 0.065, 0.68, 10);
  const count = Math.floor(length / 0.42);
  for (let i = 0; i < count; i++) {
    const roller = new THREE.Mesh(rollerGeometry, i % 3 === 0 ? electric : silver);
    roller.rotation.x = Math.PI / 2;
    roller.position.set(x - length / 2 + 0.25 + i * 0.42, -0.275, z);
    roller.castShadow = true;
    parent.add(roller);
    rollers.push(roller);
  }
  const packages: THREE.Group[] = [];
  for (let i = 0; i < 5; i++) {
    const packageGroup = new THREE.Group();
    block(packageGroup, [0.5, 0.5, 0.5], [0, 0, 0], i % 3 === 0 ? cobalt : i % 3 === 1 ? white : ice, 0.06);
    block(packageGroup, [0.25, 0.045, 0.25], [0, 0.255, 0], i % 3 === 0 ? cyan : electric, 0.014);
    parent.add(packageGroup);
    packages.push(packageGroup);
  }
  motions.push(t => {
    rollers.forEach(roller => { roller.rotation.y = t * 1.7; });
    packages.forEach((pack, i) => {
      const progress = ((t * 0.48 + i / packages.length + phase) % 1 + 1) % 1;
      pack.position.set(x - length / 2 + 0.4 + progress * (length - 0.8), 0.04 + Math.sin(t * 2 + i) * 0.018, z);
      pack.rotation.y = Math.sin(t * 0.6 + i) * 0.11;
    });
  });
}

function makeFactory(scene: THREE.Scene, camera: THREE.OrthographicCamera, motions: Motion[]) {
  const factory = new THREE.Group();
  scene.add(factory);
  block(factory, [13.5, 0.34, 8.2], [0, -0.92, 0], ice, 0.25);
  block(factory, [13.2, 0.13, 7.95], [0, -0.69, 0], white, 0.21);
  block(factory, [13.15, 0.08, 0.12], [0, -0.67, 3.92], frost, 0.04);
  for (let x = -5.8; x < 6; x += 1.45) {
    for (let z = -3.25; z < 3.5; z += 1.3) {
      if ((Math.round(x * 2 + z) % 4) === 0) block(factory, [0.3, 0.018, 0.3], [x, -0.6, z], frost, 0.012);
    }
  }

  // The two moving conveyor lanes pass through a central processing machine.
  createConveyor(factory, -2.8, 1.35, 5.65, motions, 0.06);
  createConveyor(factory, 3.05, 1.35, 5.5, motions, 0.56);
  createConveyor(factory, -1.75, -2.15, 4.85, motions, 0.32);

  // Central processor: layered physical geometry, illuminated tunnel and logo.
  block(factory, [3.8, 0.3, 3.2], [0.82, -0.38, 0], frost, 0.19);
  block(factory, [3.42, 2.23, 2.86], [0.82, 0.81, 0], white, 0.25);
  block(factory, [3.06, 0.23, 2.55], [0.82, 1.97, 0], ice, 0.08);
  for (const side of [-1, 1]) {
    block(factory, [0.27, 1.75, 2.95], [0.82 + side * 1.61, 0.79, 0], ice, 0.09);
    block(factory, [0.13, 1.51, 0.15], [0.82 + side * 1.66, 0.81, 1.52], silver, 0.04);
  }
  block(factory, [2.4, 0.91, 0.12], [0.82, 0.42, 1.48], navy, 0.11);
  block(factory, [2.16, 0.64, 0.035], [0.82, 0.42, 1.55], electric, 0.08);
  block(factory, [1.43, 1.38, 0.14], [0.82, 1.17, 1.53], cobalt, 0.13);
  block(factory, [3.04, 0.08, 0.1], [0.82, 1.83, 1.48], cobalt, 0.02);
  block(factory, [3.04, 0.07, 0.1], [0.82, -0.13, 1.48], cobalt, 0.02);
  for (const side of [-1, 1]) {
    block(factory, [0.075, 1.7, 0.11], [0.82 + side * 1.53, 0.85, 1.49], silver, 0.022);
    for (let i = 0; i < 4; i++) block(factory, [0.11, 0.04, 0.055], [0.82 + side * 1.52, 1.5 - i * 0.2, 1.55], i === 0 ? cyan : cobalt, 0.013);
  }
  // The right wall is visible in the isometric view and carries a second active interface.
  block(factory, [0.075, 1.35, 1.75], [2.57, 0.85, -0.13], cobalt, 0.055);
  for (let i = 0; i < 5; i++) {
    block(factory, [0.035, 0.075, 1.37 - i * 0.17], [2.62, 1.35 - i * 0.22, -0.13], i === 0 ? cyan : ice, 0.012);
  }
  const logo = new THREE.Mesh(new THREE.PlaneGeometry(1.15, 1.15), new THREE.MeshBasicMaterial({ map: logoTexture() }));
  logo.position.set(0.82, 1.17, 1.612);
  factory.add(logo);
  const centralLight = new THREE.PointLight(C.cyan, 12, 5, 1.5);
  centralLight.position.set(0.82, 0.55, 1.95);
  factory.add(centralLight);
  motions.push(t => { centralLight.intensity = 9.5 + Math.sin(t * 2.7) * 2.5; });

  // Side processing pods and the top data module.
  for (const [x, z, width] of [[-5.2, -1.65, 1.4], [4.8, -1.8, 1.7], [5.18, 2.25, 1.15]] as const) {
    block(factory, [width, 1.1, 1.55], [x, -0.03, z], white, 0.14);
    block(factory, [width - 0.19, 0.17, 1.41], [x, 0.62, z], ice, 0.06);
    block(factory, [0.2, 0.33, 0.1], [x, 0.07, z + 0.8], electric, 0.035);
    for (let i = 0; i < 3; i++) block(factory, [0.1, 0.035, 0.03], [x - 0.34 + i * 0.17, 0.32, z + 0.79], cyan, 0.009);
  }
  block(factory, [1.65, 1.45, 1.65], [0.82, 2.56, -0.05], cobalt, 0.17);
  block(factory, [1.42, 1.24, 1.42], [0.82, 2.58, -0.05], electric, 0.12);
  const processorFace = new THREE.Mesh(new THREE.PlaneGeometry(1.31, 0.83), new THREE.MeshBasicMaterial({ map: processorTexture() }));
  processorFace.position.set(0.82, 2.55, 0.67);
  factory.add(processorFace);
  for (const side of [-1, 1]) {
    block(factory, [0.09, 1.25, 0.08], [0.82 + side * 0.73, 2.56, 0.76], white, 0.018);
  }
  block(factory, [1.45, 0.07, 0.08], [0.82, 3.22, 0.76], white, 0.012);
  block(factory, [1.45, 0.07, 0.08], [0.82, 1.9, 0.76], white, 0.012);
  for (const side of [-1, 1]) {
    cylinder(factory, 0.37, 0.07, [0.82 + side * 0.45, 3.34, -0.05], cyan, 20);
  }

  // Industrial rails and pneumatic tubes connect visible parts of the system.
  for (const z of [-3.35, 3.3]) {
    for (let x = -5.9; x <= 5.9; x += 0.62) block(factory, [0.035, 0.5, 0.035], [x, -0.31, z], silver, 0.008);
    block(factory, [12, 0.04, 0.04], [0, -0.05, z], cobalt, 0.01);
  }
  tube(factory, [new THREE.Vector3(-5.1, 0.65, -2), new THREE.Vector3(-4.1, 1.22, -2.3), new THREE.Vector3(-2.7, 1.28, -2.3), new THREE.Vector3(-1.5, 1.88, -0.9)], 0.055, silver);
  tube(factory, [new THREE.Vector3(4.8, 0.6, -1.7), new THREE.Vector3(4.1, 1.35, -1.8), new THREE.Vector3(2.5, 1.35, -1.5), new THREE.Vector3(2.15, 1.95, -0.8)], 0.06, electric);
  tube(factory, [new THREE.Vector3(-3.1, -0.39, 3.1), new THREE.Vector3(-2.2, 0.45, 3.1), new THREE.Vector3(-1.1, 0.45, 2.7), new THREE.Vector3(-0.5, 0.92, 1.4)], 0.045, silver);

  // Repeating mechanical details make motion legible at a glance.
  const rotors: THREE.Group[] = [];
  for (const x of [-4.7, -3.8, 4.7]) {
    const rotor = new THREE.Group();
    rotor.position.set(x, 0.86, -2.85);
    cylinder(rotor, 0.2, 0.13, [0, 0, 0], cobalt);
    for (let i = 0; i < 4; i++) {
      const blade = block(rotor, [0.35, 0.045, 0.08], [0.23, 0.08, 0], ice, 0.018);
      blade.rotation.y = i * Math.PI / 2;
      blade.position.set(Math.cos(i * Math.PI / 2) * 0.23, 0.08, Math.sin(i * Math.PI / 2) * 0.23);
    }
    factory.add(rotor);
    rotors.push(rotor);
  }
  motions.push(t => rotors.forEach((rotor, i) => { rotor.rotation.y = t * (i % 2 ? -1.5 : 1.5); }));

  createRobotArm(factory, 4.05, -2.55, motions);
  createWorker(factory, -4.35, 2.8, motions, 0.4);
  createWorker(factory, -2.9, -2.8, motions, 1.8);
  createWorker(factory, 5.7, 1.05, motions, 2.7);

  const cart = new THREE.Group();
  factory.add(cart);
  block(cart, [1.12, 0.38, 0.72], [0, -0.3, 0], cobalt, 0.12);
  block(cart, [0.94, 0.11, 0.55], [0, -0.05, 0], ice, 0.06);
  for (const x of [-0.38, 0.38]) for (const z of [-0.3, 0.3]) cylinder(cart, 0.14, 0.08, [x, -0.47, z], navy, 12).rotation.x = Math.PI / 2;
  cylinder(cart, 0.11, 0.32, [0, 0.17, 0], white);
  sphere(cart, 0.21, [0, 0.46, 0], white);
  block(cart, [0.32, 0.1, 0.035], [0, 0.47, 0.2], electric, 0.018);
  motions.push(t => {
    cart.position.set(-5.6 + ((t * 0.56) % 11.2), -0.02 + Math.sin(t * 3) * 0.01, 3.04);
    cart.rotation.y = Math.sin(t * 0.48) * 0.045;
  });

  const panelData: [string, number, number, number][] = [
    ['PLAN', -2.8, 2.15, -2.45],
    ['DESIGN', -3.95, 0.95, 0.4],
    ['DEVELOP', 3.55, 1.95, -1.8],
    ['DEPLOY', 4.07, 0.55, 1.85],
    ['SCALE', 5.6, 1.38, 2.38],
  ];
  panelData.forEach(([label, x, y, z], index) => createPanel(factory, camera, label, index, x, y, z, motions));

  // Small orbiting data cubes establish depth around the main machine.
  const dataCubes: THREE.Group[] = [];
  for (let i = 0; i < 4; i++) {
    const data = new THREE.Group();
    block(data, [0.35, 0.35, 0.35], [0, 0, 0], i % 2 ? white : electric, 0.045);
    block(data, [0.14, 0.01, 0.14], [0, 0.18, 0], cyan, 0.005);
    factory.add(data);
    dataCubes.push(data);
  }
  motions.push(t => dataCubes.forEach((cube, i) => {
    cube.position.set(0.82 + Math.cos(t * 0.47 + i * Math.PI / 2) * 2.3, 2.18 + Math.sin(t * 1.2 + i) * 0.18, Math.sin(t * 0.47 + i * Math.PI / 2) * 1.8);
    cube.rotation.y = t * 0.7 + i;
    cube.rotation.z = Math.sin(t + i) * 0.15;
  }));
}

function createDevice(parent: THREE.Object3D, width: number, height: number, texture: THREE.Texture, x = 0, y = 0, z = 0) {
  const device = new THREE.Group();
  device.position.set(x, y, z);
  parent.add(device);
  block(device, [width, height, 0.16], [0, 0, 0], navy, 0.18);
  block(device, [width - 0.12, height - 0.12, 0.025], [0, 0, 0.09], deep, 0.12);
  const screen = new THREE.Mesh(new THREE.PlaneGeometry(width - 0.19, height - 0.19), new THREE.MeshBasicMaterial({ map: texture, side: THREE.DoubleSide }));
  screen.position.z = 0.107;
  device.add(screen);
  cylinder(device, 0.025, 0.025, [0, height / 2 - 0.045, 0.12], silver, 10).rotation.x = Math.PI / 2;
  return device;
}

function makeProject(scene: THREE.Scene, kind: ProjectKind, motions: Motion[]) {
  const root = new THREE.Group();
  scene.add(root);
  block(root, [5.2, 0.2, 3.8], [0, -1.73, 0], new THREE.MeshStandardMaterial({ color: 0xacc5f4, roughness: 0.8, transparent: true, opacity: 0.75 }), 0.23);
  for (let i = 0; i < 5; i++) {
    block(root, [0.35, 0.25 + i * 0.12, 0.35], [-2.25 + i * 1.1, -1.48 + i * 0.06, -1.25], i % 2 ? frost : ice, 0.06);
  }

  if (kind === 'operations') {
    const tablet = createDevice(root, 3.7, 2.31, dashboardTexture(kind), -0.28, 0.05, 0);
    tablet.rotation.set(-0.1, -0.23, -0.12);
    block(root, [1.55, 0.08, 0.65], [-0.04, -1.3, 0.65], silver, 0.04);
    lineBetween(root, new THREE.Vector3(-0.4, -1.26, 0.65), new THREE.Vector3(-0.4, -1.1, 0.15), 0.055, silver);
    const status = sphere(root, 0.13, [1.85, 0.87, 0.4], cyan);
    motions.push(t => {
      tablet.position.y = 0.05 + Math.sin(t * 0.8) * 0.06;
      tablet.rotation.y = -0.23 + Math.sin(t * 0.65) * 0.04;
      status.scale.setScalar(0.85 + Math.sin(t * 2.4) * 0.2);
    });
  } else if (kind === 'dashboard') {
    const back = createDevice(root, 2.1, 2.83, phoneTexture(kind), -0.66, -0.04, -0.36);
    back.rotation.y = -0.32;
    const front = createDevice(root, 1.58, 2.53, phoneTexture(kind), 0.78, -0.13, 0.52);
    front.rotation.y = 0.2;
    const rings = new THREE.Group();
    rings.position.set(1.64, 0.68, -0.4);
    for (let i = 0; i < 3; i++) {
      const ring = new THREE.Mesh(new THREE.TorusGeometry(0.2 + i * 0.16, 0.015, 6, 48), i % 2 ? cyan : electric);
      ring.rotation.x = 0.7;
      rings.add(ring);
    }
    root.add(rings);
    motions.push(t => {
      back.position.y = -0.04 + Math.sin(t * 0.7) * 0.05;
      front.position.y = -0.13 + Math.sin(t * 0.7 + 1.6) * 0.055;
      front.rotation.y = 0.2 + Math.sin(t * 0.55) * 0.045;
      rings.rotation.y = t * 0.4;
    });
  } else {
    const phone = createDevice(root, 2.02, 3.17, phoneTexture(kind), 0.28, 0.06, 0.06);
    phone.rotation.set(-0.05, -0.16, -0.12);
    const pin = new THREE.Group();
    pin.position.set(1.22, 0.42, 0.66);
    cylinder(pin, 0.08, 0.39, [0, -0.15, 0], cobalt, 16);
    sphere(pin, 0.23, [0, 0.14, 0], electric);
    sphere(pin, 0.09, [0, 0.14, 0.202], white);
    root.add(pin);
    const beacons: THREE.Mesh[] = [];
    for (let i = 0; i < 3; i++) {
      const beacon = new THREE.Mesh(new THREE.TorusGeometry(0.17 + i * 0.12, 0.012, 5, 40), cyan);
      beacon.position.set(1.22, 0.22, 0.66);
      beacon.rotation.x = Math.PI / 2;
      root.add(beacon);
      beacons.push(beacon);
    }
    motions.push(t => {
      phone.position.y = 0.06 + Math.sin(t * 0.7) * 0.055;
      phone.rotation.y = -0.16 + Math.sin(t * 0.51) * 0.04;
      pin.position.y = 0.42 + Math.sin(t * 1.4) * 0.09;
      beacons.forEach((beacon, i) => {
        const scale = 0.82 + ((t * 0.55 + i / 3) % 1) * 0.7;
        beacon.scale.setScalar(scale);
      });
    });
  }
}

function mountScene(canvas: HTMLCanvasElement, kind: 'factory' | ProjectKind) {
  let renderer: THREE.WebGLRenderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true, powerPreference: 'high-performance' });
  } catch {
    canvas.dataset.webglUnavailable = 'true';
    return () => undefined;
  }
  renderer.setClearColor(0xffffff, 0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = kind === 'factory' ? 1.14 : 1.2;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFShadowMap;

  const scene = new THREE.Scene();
  const camera = new THREE.OrthographicCamera(-7, 7, 5, -5, 0.1, 100);
  if (kind === 'factory') camera.position.set(12.8, 11.2, 16.6);
  else camera.position.set(7.2, 5.6, 9.8);
  camera.lookAt(kind === 'factory' ? new THREE.Vector3(0, 1.7, 0) : new THREE.Vector3(0, -0.05, 0));
  scene.add(new THREE.AmbientLight(0xffffff, kind === 'factory' ? 1.05 : 1.35));
  const sun = new THREE.DirectionalLight(0xffffff, kind === 'factory' ? 2.9 : 2.6);
  sun.position.set(-6, 12, 9);
  sun.castShadow = true;
  sun.shadow.mapSize.set(kind === 'factory' ? 2048 : 1024, kind === 'factory' ? 2048 : 1024);
  sun.shadow.camera.left = -11;
  sun.shadow.camera.right = 11;
  sun.shadow.camera.top = 11;
  sun.shadow.camera.bottom = -11;
  sun.shadow.bias = -0.0003;
  sun.shadow.radius = 3;
  scene.add(sun);
  const fill = new THREE.DirectionalLight(0x7baefb, kind === 'factory' ? 0.95 : 1.35);
  fill.position.set(8, 6, -8);
  scene.add(fill);

  const motions: Motion[] = [];
  const cancelOffice = kind === 'factory' ? loadOffice(scene, camera, canvas, motions, () => {
    prepare();
  }) : () => undefined;
  if (kind !== 'factory') makeProject(scene, kind, motions);

  const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  let reduceMotion = motionQuery.matches;
  let visible = true;
  let raf = 0;
  let disposed = false;
  let prepared = false;
  let preparing = false;
  let compilation: Promise<THREE.Object3D> | undefined;
  let cancelPreparation = () => {};
  let cancelFirstRender = () => {};
  let startTime = performance.now();
  let lastFrame = 0;
  let lastSeconds = 0;
  const targetInterval = kind === 'factory' ? 1000 / 60 : 1000 / 30;

  function resize() {
    const width = Math.max(1, canvas.clientWidth);
    const height = Math.max(1, canvas.clientHeight);
    const pixelRatio = Math.min(window.devicePixelRatio || 1, kind === 'factory' ? 1.6 : 1.4);
    renderer.setPixelRatio(pixelRatio);
    renderer.setSize(width, height, false);
    const aspect = width / height;
    const viewHeight = kind === 'factory' ? Math.max(11.6, 15.4 / aspect) : Math.max(5.8, 5.4 / aspect);
    camera.left = -viewHeight * aspect / 2;
    camera.right = viewHeight * aspect / 2;
    camera.top = viewHeight / 2;
    camera.bottom = -viewHeight / 2;
    camera.updateProjectionMatrix();
    motions.forEach(motion => motion(reduceMotion ? 0 : lastSeconds));
    if (prepared) renderer.render(scene, camera);
  }

  function prepare() {
    if (disposed || preparing) return;
    preparing = true;
    canvas.dataset.sceneState = 'preparing';
    // Let the driver compile programs without stalling the first visible
    // frame. In particular, physical glass and skinned meshes have many variants.
    cancelPreparation = whenScrollIdle(() => {
      compilation = renderer.compileAsync(scene, camera);
      compilation.then(() => {
        if (disposed) return;
        cancelFirstRender = whenScrollIdle(() => {
          if (disposed) return;
          prepared = true;
          renderer.render(scene, camera);
          canvas.dataset.sceneState = 'ready';
          if (kind === 'factory') {
            canvas.dataset.modelLoaded = 'true';
            canvas.dataset.modelState = 'ready';
          }
          start();
        });
      }).catch(error => {
        if (disposed) return;
        canvas.dataset.sceneState = 'error';
        console.error('Unable to prepare the 3D scene.', error);
      });
    });
  }

  function tick(now: number) {
    if (disposed || !visible || reduceMotion || document.hidden) { raf = 0; return; }
    raf = requestAnimationFrame(tick);
    if (now - lastFrame < targetInterval) return;
    lastFrame = now;
    const seconds = (now - startTime) / 1000;
    lastSeconds = seconds;
    motions.forEach(motion => motion(seconds));
    renderer.render(scene, camera);
  }

  function start() {
    if (disposed || !prepared || raf || !visible || reduceMotion || document.hidden) return;
    startTime = performance.now() - (lastFrame ? lastFrame - startTime : 0);
    raf = requestAnimationFrame(tick);
  }

  const observer = new ResizeObserver(resize);
  observer.observe(canvas);
  resize();
  const visibilityObserver = new IntersectionObserver(entries => {
    visible = entries[0]?.isIntersecting ?? true;
    if (visible) start();
    else if (raf) { cancelAnimationFrame(raf); raf = 0; }
  }, { rootMargin: '100px' });
  visibilityObserver.observe(canvas);
  const onDocumentVisibility = () => { if (!document.hidden) start(); else if (raf) { cancelAnimationFrame(raf); raf = 0; } };
  const onMotionChange = () => {
    reduceMotion = motionQuery.matches;
    if (reduceMotion) {
      if (raf) cancelAnimationFrame(raf);
      raf = 0;
      motions.forEach(motion => motion(0));
      if (prepared) renderer.render(scene, camera);
    } else start();
  };
  document.addEventListener('visibilitychange', onDocumentVisibility);
  motionQuery.addEventListener('change', onMotionChange);
  if (kind !== 'factory') prepare();

  return () => {
    disposed = true;
    cancelPreparation();
    cancelFirstRender();
    cancelOffice();
    if (raf) cancelAnimationFrame(raf);
    observer.disconnect();
    visibilityObserver.disconnect();
    document.removeEventListener('visibilitychange', onDocumentVisibility);
    motionQuery.removeEventListener('change', onMotionChange);
    const release = () => {
      const geometries = new Set<THREE.BufferGeometry>();
      const materials = new Set<THREE.Material>();
      const textures = new Set<THREE.Texture>();
      scene.traverse(object => {
        if (!(object instanceof THREE.Mesh)) return;
        geometries.add(object.geometry);
        (Array.isArray(object.material) ? object.material : [object.material]).forEach(material => {
          materials.add(material);
          const map = (material as THREE.MeshBasicMaterial).map;
          if (map) textures.add(map);
        });
      });
      geometries.forEach(geometry => geometry.dispose());
      textures.forEach(texture => texture.dispose());
      // Shared palette materials are module-wide and are reused by other canvases.
      materials.forEach(material => {
        if (![white, ice, frost, silver, cobalt, electric, cyan, navy, deep].includes(material as THREE.MeshStandardMaterial)) material.dispose();
      });
      renderer.dispose();
    };
    // compileAsync polls material programs; keep them alive until that completes.
    if (compilation) compilation.then(release, release);
    else release();
  };
}

export function mountFactoryScene(canvas: HTMLCanvasElement) {
  return mountScene(canvas, 'factory');
}

export function mountProjectScene(canvas: HTMLCanvasElement, kind: ProjectKind) {
  return mountScene(canvas, kind);
}
