import * as THREE from 'three';
import { GLTFLoader, type GLTF } from 'three/addons/loaders/GLTFLoader.js';
import { whenScrollIdle } from './scroll-idle';

type Motion = (seconds: number) => void;

function disposeModel(root: THREE.Object3D) {
  const materials = new Set<THREE.Material>();
  root.traverse((object) => {
    if (!(object instanceof THREE.Mesh)) return;
    object.geometry.dispose();
    (Array.isArray(object.material) ? object.material : [object.material]).forEach(m => materials.add(m));
  });
  materials.forEach(m => m.dispose());
}

// The GLB is static. Connected surfaces let us assign joints while retaining
// its original sculpted character, clothes, face, and materials.
function surfaceCenters(geometry: THREE.BufferGeometry) {
  const positions = geometry.getAttribute('position');
  const parents = Array.from({ length: positions.count }, (_, i) => i);
  const root = (value: number): number => {
    while (parents[value] !== value) {
      parents[value] = parents[parents[value]];
      value = parents[value];
    }
    return value;
  };
  const join = (a: number, b: number) => { parents[root(a)] = root(b); };
  const vertices = new Map<string, number>();
  for (let i = 0; i < positions.count; i++) {
    const key = [positions.getX(i), positions.getY(i), positions.getZ(i)].map(v => Math.round(v * 100000)).join(',');
    const existing = vertices.get(key);
    if (existing !== undefined) join(i, existing);
    else vertices.set(key, i);
  }
  const index = geometry.index;
  const at = (i: number) => index ? index.getX(i) : i;
  for (let i = 0; i < (index?.count ?? positions.count); i += 3) {
    join(at(i), at(i + 1));
    join(at(i), at(i + 2));
  }
  const boxes = new Map<number, THREE.Box3>();
  const point = new THREE.Vector3();
  for (let i = 0; i < positions.count; i++) {
    const key = root(i);
    if (!boxes.has(key)) boxes.set(key, new THREE.Box3());
    boxes.get(key)!.expandByPoint(point.fromBufferAttribute(positions, i));
  }
  const centers = new Map([...boxes].map(([key, box]) => [key, box.getCenter(new THREE.Vector3())]));
  return parents.map((_, i) => centers.get(root(i))!);
}

function makeCallAnimation(office: THREE.Object3D, camera: THREE.Camera, canvas: HTMLCanvasElement) {
  const character = office.getObjectByName('25_Character_Thinking');
  if (!character) throw new Error('The office model is missing its lounge character.');
  const rig = new THREE.Group();
  rig.name = 'ClientCallCharacter';
  character.parent!.add(rig);
  const bones: THREE.Bone[] = [];
  const joint = (name: string, parent: THREE.Object3D, x: number, y: number, z = 0) => {
    const bone = new THREE.Bone();
    bone.name = name;
    bone.position.set(x, y, z);
    parent.add(bone);
    bones.push(bone);
    return bone;
  };
  const torso = joint('Torso', rig, 0, 1.15);
  const head = joint('Head', torso, 0, .65);
  const rightArm = joint('PhoneArm', torso, .26, .5);
  const leftArm = joint('GestureArm', torso, -.26, .5);
  const rightLeg = joint('RightThigh', rig, .16, 1.15);
  const rightKnee = joint('RightKnee', rightLeg, 0, -.35);
  const leftLeg = joint('LeftThigh', rig, -.16, 1.15);
  const leftKnee = joint('LeftKnee', leftLeg, 0, -.35);
  const skeleton = new THREE.Skeleton(bones);
  const meshes: THREE.SkinnedMesh[] = [];

  for (const object of [...character.children]) {
    if (!(object instanceof THREE.Mesh)) continue;
    object.updateMatrix();
    const geometry = object.geometry.clone().applyMatrix4(object.matrix);
    const positions = geometry.getAttribute('position');
    const centers = surfaceCenters(geometry);
    const indices = new Uint16Array(positions.count * 4);
    const weights = new Float32Array(positions.count * 4);
    for (let i = 0; i < positions.count; i++) {
      const center = centers[i];
      let bone = 0;
      let kneeWeight = 0;
      if (center.y < 1.18 && Math.abs(center.x) > .04) {
        bone = center.x > 0 ? 4 : 6;
        kneeWeight = 1 - THREE.MathUtils.smoothstep(positions.getY(i), .76, .87);
      } else if (object.name.includes('Ceramic') && Math.abs(center.x) > .22) {
        bone = center.x > 0 ? 2 : 3;
      } else if (object.name.includes('Skin') && Math.abs(center.x) > .075 && center.z > .14 && center.y < 2.03) {
        bone = center.x > 0 ? 2 : 3;
      } else if (center.y > 1.76) bone = 1;
      indices[i * 4] = bone;
      indices[i * 4 + 1] = bone + (kneeWeight > 0 ? 1 : 0);
      weights[i * 4] = 1 - kneeWeight;
      weights[i * 4 + 1] = kneeWeight;
    }
    geometry.setAttribute('skinIndex', new THREE.Uint16BufferAttribute(indices, 4));
    geometry.setAttribute('skinWeight', new THREE.Float32BufferAttribute(weights, 4));
    const mesh = new THREE.SkinnedMesh(geometry, object.material);
    mesh.castShadow = mesh.receiveShadow = true;
    mesh.frustumCulled = false;
    rig.add(mesh);
    meshes.push(mesh);
    object.geometry.dispose();
  }
  character.removeFromParent();
  rig.updateMatrixWorld(true);
  meshes.forEach(mesh => mesh.bind(skeleton));

  const phone = new THREE.Mesh(new THREE.BoxGeometry(.09, .22, .035),
    new THREE.MeshStandardMaterial({ color: 0x182431, roughness: .35 }));
  // Original hand rests near the chin. Its shoulder carries the phone to the ear.
  phone.position.set(-.11, .34, .22);
  phone.rotation.set(.08, -.25, -.08);
  phone.castShadow = true;
  rightArm.add(phone);
  const screen = new THREE.Mesh(new THREE.PlaneGeometry(.064, .17), new THREE.MeshBasicMaterial({ color: 0x82dab0 }));
  screen.position.z = .018;
  phone.add(screen);

  const bubble = document.createElement('div');
  bubble.className = 'call-bubble';
  bubble.hidden = true;
  bubble.setAttribute('aria-hidden', 'true');
  bubble.innerHTML = '<span class="call-bubble-label"></span><span class="call-bubble-message"></span>';
  canvas.parentElement!.append(bubble);
  const label = bubble.querySelector<HTMLElement>('.call-bubble-label')!;
  const message = bubble.querySelector<HTMLElement>('.call-bubble-message')!;
  const anchor = new THREE.Vector3();
  let previousStage = 'initial';
  const smooth = (t: number, from: number, to: number) => THREE.MathUtils.smoothstep(t, from, to);

  const update: Motion = (seconds) => {
    const t = seconds % 20;
    const rise = smooth(t, 4.2, 5.8) * (1 - smooth(t, 16.6, 18.4));
    const step = smooth(t, 5.5, 6.8) * (1 - smooth(t, 15.7, 17));
    const call = smooth(t, 4.5, 6.2) * (1 - smooth(t, 14.8, 16));
    const talking = smooth(t, 6.4, 7) * (1 - smooth(t, 14.4, 15));
    rig.position.set(-3.52 + .8 * step, -.30 * (1 - rise), -1.53 + .65 * step);
    rig.rotation.y = .1 + .22 * step;
    torso.rotation.x = -.1 * (1 - rise) + Math.sin(rise * Math.PI) * .18;
    torso.rotation.z = Math.sin(t * 1.8) * .012 * talking;
    rightLeg.rotation.x = leftLeg.rotation.x = -1.38 * (1 - rise);
    rightKnee.rotation.x = leftKnee.rotation.x = 1.38 * (1 - rise);
    rightLeg.rotation.x += Math.sin(step * Math.PI * 2) * .12;
    leftLeg.rotation.x -= Math.sin(step * Math.PI * 2) * .12;
    rightArm.rotation.z = -.31 * call;
    rightArm.rotation.x = 1.5 * (1 - call) - .12 * call;
    leftArm.rotation.z = (.13 + Math.sin(t * 2.5) * .1) * talking;
    leftArm.rotation.x = -.16 * talking;
    head.rotation.x = .04 * (1 - rise) + Math.sin(t * 3) * .035 * talking;
    head.rotation.y = -.1 * talking;
    phone.rotation.z = -.08 + (t >= 3 && t < 4.5 ? Math.sin(t * 48) * .1 : 0);

    let stage = '';
    let speaker = '';
    let text = '';
    if (t >= 3 && t < 5) { stage = 'ringing'; speaker = 'INCOMING CALL'; text = 'Client is calling…'; }
    else if (t >= 6.3 && t < 8.8) { stage = 'studio'; speaker = 'NODEWORKS'; text = 'Hi! How can we help?'; }
    else if (t >= 8.8 && t < 11.2) { stage = 'client'; speaker = 'CLIENT'; text = 'Let’s build our next platform.'; }
    else if (t >= 11.2 && t < 13.2) { stage = 'proposal'; speaker = 'NODEWORKS'; text = 'We’ll make it happen.'; }
    else if (t >= 13.2 && t < 15.7) { stage = 'deal'; speaker = 'PROJECT CONFIRMED'; text = 'Deal! Let’s get started. ✓'; }
    if (stage !== previousStage) {
      previousStage = stage;
      bubble.hidden = !stage;
      bubble.dataset.stage = stage;
      label.textContent = speaker;
      message.textContent = text;
    }
    canvas.dataset.callStage = stage || (rise > .1 ? 'returning' : 'seated');
    if (stage) {
      rig.updateWorldMatrix(true, true);
      anchor.set(0, 2.5, 0).applyMatrix4(rig.matrixWorld).project(camera);
      bubble.style.left = `${(anchor.x * .5 + .5) * canvas.clientWidth}px`;
      bubble.style.top = `${(-anchor.y * .5 + .5) * canvas.clientHeight}px`;
    }
  };
  update(0);
  return { update, dispose: () => { bubble.remove(); skeleton.dispose(); } };
}

export function loadOffice(scene: THREE.Scene, camera: THREE.Camera, canvas: HTMLCanvasElement, motions: Motion[], onLoad: () => void) {
  let cancelled = false;
  let cleanup = () => undefined as void;
  let cancelParse = () => {};
  const request = new AbortController();
  canvas.dataset.modelState = 'loading';
  const onModel = (gltf: GLTF) => {
    if (cancelled) { disposeModel(gltf.scene); return; }
    gltf.scene.traverse((object) => {
      if (object instanceof THREE.Mesh) {
        object.castShadow = true;
        object.receiveShadow = true;
      }
    });
    scene.add(gltf.scene);
    const animation = makeCallAnimation(gltf.scene, camera, canvas);
    // Always start seated, including after a slow model download.
    let start: number | undefined;
    const motion: Motion = (seconds) => { start ??= seconds; animation.update(Math.max(0, seconds - start)); };
    motions.push(motion);
    cleanup = () => { motions.splice(motions.indexOf(motion), 1); animation.dispose(); };
    canvas.dataset.modelState = 'preparing';
    onLoad();
  };
  const onError = (error: unknown) => {
    if (cancelled) return;
    canvas.dataset.modelState = 'error';
    console.error('Unable to load the Nodeworks office model.', error);
    const errorLabel = document.createElement('p');
    errorLabel.className = 'scene-error';
    errorLabel.textContent = 'The studio preview could not load. Please refresh to try again.';
    canvas.parentElement!.append(errorLabel);
    cleanup = () => errorLabel.remove();
  };
  // Download immediately, but avoid decoding the large GLB during a gesture.
  fetch(`${import.meta.env.BASE_URL}models/nodeworks-latest.glb`, { signal: request.signal })
    .then(response => {
      if (!response.ok) throw new Error(`Office model request failed (${response.status}).`);
      return response.arrayBuffer();
    })
    .then(buffer => {
      if (cancelled) return;
      cancelParse = whenScrollIdle(() => {
        new GLTFLoader().parse(buffer, `${import.meta.env.BASE_URL}models/`, onModel, onError);
      });
    })
    .catch(onError);
  return () => { cancelled = true; request.abort(); cancelParse(); cleanup(); };
}
