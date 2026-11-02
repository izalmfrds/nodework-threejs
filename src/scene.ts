import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { RectAreaLightUniformsLib } from 'three/addons/lights/RectAreaLightUniformsLib.js';
import { loadOffice } from './office';
import { whenScrollIdle } from './scroll-idle';

export function mountFactoryScene(canvas: HTMLCanvasElement) {
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
  renderer.toneMappingExposure = 1;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.shadowMap.autoUpdate = false;

  const scene = new THREE.Scene();
  scene.environmentIntensity = .25;
  const target = new THREE.Vector3(0, 3, 0);
  const defaultDirection = new THREE.Vector3(.34, .09, 1).normalize();
  const cameraRadius = 30;
  const stage = canvas.closest<HTMLElement>('.hero-stage')!;
  const camera = new THREE.PerspectiveCamera(30, 1, .1, 120);
  camera.position.copy(target).addScaledVector(defaultDirection, 30);
  camera.lookAt(target);
  scene.add(new THREE.AmbientLight(0xffffff, .4));
  scene.add(new THREE.HemisphereLight(0xeaf3ff, 0x8296b8, .6));
  const sun = new THREE.DirectionalLight(0xfff6eb, 2.4);
  sun.position.set(-6, 20, 10);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, { left: -13, right: 13, top: 13, bottom: -13 });
  sun.shadow.bias = -.0003;
  sun.shadow.normalBias = .015;
  scene.add(sun);
  const fill = new THREE.DirectionalLight(0x83b4ff, .5);
  fill.position.set(10, 9, -5);
  scene.add(fill);
  RectAreaLightUniformsLib.init();
  const pendant = new THREE.RectAreaLight(0xd9efff, 6, 4.3, .55);
  pendant.position.set(0, 5.82, -2.6);
  pendant.lookAt(0, 0, -3.4);
  scene.add(pendant);
  const interiorBounce = new THREE.PointLight(0xe3efff, 9, 8, 2);
  interiorBounce.position.set(0, 5.55, -1.5);
  scene.add(interiorBounce);
  for (const x of [-4.6, 4.6]) {
    const light = new THREE.SpotLight(0xe2f1ff, 80, 13, .95, 1, 2);
    light.position.set(x, 6.24, -1.8);
    light.target.position.set(x * .8, .3, .8);
    light.castShadow = true;
    light.shadow.mapSize.set(1024, 1024);
    light.shadow.normalBias = .025;
    scene.add(light, light.target);
  }
  for (const x of [-4.4, 4.4]) {
    const led = new THREE.PointLight(0x168dff, 6, 3, 2);
    led.position.set(x, .32, 4.9);
    scene.add(led);
  }

  // No perpetual render loop: a static assembly redraws only when its view changes.
  const controls = new OrbitControls(camera, canvas);
  controls.target.copy(target);
  controls.enableZoom = false;
  controls.enablePan = false;
  controls.enableDamping = false;
  controls.rotateSpeed = .45;
  controls.minAzimuthAngle = -Math.PI / 4;
  controls.maxAzimuthAngle = Math.PI / 4;
  controls.minPolarAngle = THREE.MathUtils.degToRad(60);
  controls.maxPolarAngle = THREE.MathUtils.degToRad(88);
  controls.mouseButtons = { LEFT: THREE.MOUSE.ROTATE, MIDDLE: null, RIGHT: null };
  controls.update();
  canvas.style.touchAction = 'pan-y';

  let disposed = false;
  let prepared = false;
  let preparing = false;
  let compilation: Promise<THREE.Object3D> | undefined;
  let environment: THREE.WebGLRenderTarget | undefined;
  let cancelPreparation = () => {};
  let cancelFirstRender = () => {};
  let framingPoints: THREE.Vector3[] = [];
  for (const x of [-8, 8]) for (const y of [0, 6.7]) for (const z of [-5, 5]) {
    framingPoints.push(new THREE.Vector3(x, y, z));
  }
  let fitting = false;
  const draw = () => {
    if (prepared && !disposed && !document.hidden) renderer.render(scene, camera);
  };
  const updateViewState = () => {
    if (fitting) return;
    fitView(camera.position.clone().sub(target).normalize());
  };
  const reportView = () => {
    canvas.dataset.viewAzimuth = controls.getAzimuthalAngle().toFixed(3);
    canvas.dataset.viewElevation = (Math.PI / 2 - controls.getPolarAngle()).toFixed(3);
    draw();
  };
  controls.addEventListener('change', updateViewState);
  controls.addEventListener('start', () => { canvas.dataset.dragging = 'true'; });
  controls.addEventListener('end', () => { delete canvas.dataset.dragging; });
  // Let a vertical touch scroll the page. Mobile users have explicit view buttons.
  const onPointerDown = (event: PointerEvent) => { controls.enabled = event.pointerType === 'mouse'; };
  canvas.addEventListener('pointerdown', onPointerDown, true);

  function projectedBounds(direction: THREE.Vector3) {
    camera.position.copy(target).addScaledVector(direction.clone().normalize(), cameraRadius);
    camera.lookAt(target);
    const inverseRotation = camera.quaternion.clone().invert();
    let left = Infinity, right = -Infinity, bottom = Infinity, top = -Infinity;
    for (const point of framingPoints) {
      const view = point.clone().sub(target).applyQuaternion(inverseRotation);
      const depth = cameraRadius - view.z;
      left = Math.min(left, view.x / depth);
      right = Math.max(right, view.x / depth);
      bottom = Math.min(bottom, view.y / depth);
      top = Math.max(top, view.y / depth);
    }
    return { left, right, bottom, top };
  }
  function desiredWidth() {
    return Math.min(window.innerWidth * (window.innerWidth > 900 ? .8 : .92), canvas.clientWidth * .96);
  }
  function viewPadding() {
    return window.innerWidth > 900 ? { top: 16, bottom: 4 } : { top: 16, bottom: 56 };
  }
  function fitView(direction: THREE.Vector3) {
    if (fitting) return;
    fitting = true;
    const bounds = projectedBounds(direction);
    const width = Math.max(1, canvas.clientWidth), height = Math.max(1, canvas.clientHeight);
    const padding = viewPadding();
    const focal = Math.min(desiredWidth() / (bounds.right - bounds.left), (height - padding.top - padding.bottom) / (bounds.top - bounds.bottom));
    camera.fov = THREE.MathUtils.radToDeg(2 * Math.atan(height / (2 * focal)));
    camera.aspect = width / height;
    // An off-axis lens centres the actual silhouette without changing the chosen angle.
    camera.setViewOffset(width, height, focal * (bounds.left + bounds.right) / 2,
      (padding.bottom - padding.top) / 2 - focal * (bounds.top + bounds.bottom) / 2, width, height);
    controls.update();
    camera.updateProjectionMatrix();
    canvas.dataset.modelWidthRatio = ((bounds.right - bounds.left) * focal / window.innerWidth).toFixed(3);
    fitting = false;
    reportView();
  }
  function resize() {
    const direction = camera.position.clone().sub(target).normalize();
    const bounds = projectedBounds(defaultDirection);
    const padding = viewPadding();
    const requiredHeight = Math.ceil(desiredWidth() * (bounds.top - bounds.bottom) / (bounds.right - bounds.left) + padding.top + padding.bottom);
    if (stage.style.height !== `${requiredHeight}px`) stage.style.height = `${requiredHeight}px`;
    const width = Math.max(1, canvas.clientWidth);
    const height = Math.max(1, canvas.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.6));
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    fitView(direction);
  }
  const spherical = new THREE.Spherical();
  function rotateView(horizontal: number, vertical = 0) {
    spherical.setFromVector3(camera.position.clone().sub(target));
    spherical.theta = THREE.MathUtils.clamp(spherical.theta + horizontal, controls.minAzimuthAngle, controls.maxAzimuthAngle);
    spherical.phi = THREE.MathUtils.clamp(spherical.phi + vertical, controls.minPolarAngle, controls.maxPolarAngle);
    fitView(new THREE.Vector3().setFromSpherical(spherical).normalize());
  }
  const actions = canvas.closest('.hero-stage')!.querySelectorAll<HTMLButtonElement>('[data-scene-view]');
  const onViewAction = (event: Event) => {
    const action = (event.currentTarget as HTMLButtonElement).dataset.sceneView;
    if (action === 'reset') fitView(defaultDirection.clone());
    else rotateView(action === 'left' ? -.14 : .14);
  };
  actions.forEach(button => button.addEventListener('click', onViewAction));
  const onKeyDown = (event: KeyboardEvent) => {
    const keys: Record<string, [number, number]> = {
      ArrowLeft: [-.12, 0], ArrowRight: [.12, 0], ArrowUp: [0, -.06], ArrowDown: [0, .06],
    };
    if (event.key === 'Home') { event.preventDefault(); fitView(defaultDirection.clone()); }
    else if (keys[event.key]) { event.preventDefault(); rotateView(...keys[event.key]); }
  };
  canvas.addEventListener('keydown', onKeyDown);

  function prepare() {
    if (disposed || preparing) return;
    preparing = true;
    framingPoints = scene.getObjectByName('Nodeworks / supplied asset assembly')!.userData.framingPoints;
    resize();
    canvas.dataset.sceneState = 'preparing';
    cancelPreparation = whenScrollIdle(() => {
      const room = new RoomEnvironment();
      const generator = new THREE.PMREMGenerator(renderer);
      environment = generator.fromScene(room, .04);
      scene.environment = environment.texture;
      room.dispose();
      generator.dispose();
      compilation = renderer.compileAsync(scene, camera);
      compilation.then(() => {
        if (disposed) return;
        cancelFirstRender = whenScrollIdle(() => {
          if (disposed) return;
          prepared = true;
          renderer.shadowMap.needsUpdate = true;
          renderer.render(scene, camera);
          canvas.dataset.sceneState = 'ready';
          canvas.dataset.modelLoaded = 'true';
          canvas.dataset.modelState = 'ready';
        });
      }).catch(error => {
        if (disposed) return;
        canvas.dataset.sceneState = 'error';
        console.error('Unable to prepare the 3D scene.', error);
      });
    });
  }
  const observer = new ResizeObserver(resize);
  observer.observe(canvas);
  resize();
  const cancelOffice = loadOffice(scene, canvas, prepare);
  document.addEventListener('visibilitychange', draw);

  return () => {
    disposed = true;
    cancelPreparation();
    cancelFirstRender();
    cancelOffice();
    observer.disconnect();
    controls.removeEventListener('change', updateViewState);
    controls.dispose();
    actions.forEach(button => button.removeEventListener('click', onViewAction));
    canvas.removeEventListener('pointerdown', onPointerDown, true);
    canvas.removeEventListener('keydown', onKeyDown);
    document.removeEventListener('visibilitychange', draw);
    const release = () => {
      const geometries = new Set<THREE.BufferGeometry>();
      const materials = new Set<THREE.Material>();
      scene.traverse(object => {
        if (object instanceof THREE.Light) object.dispose();
        if (!(object instanceof THREE.Mesh) && !(object instanceof THREE.Sprite)) return;
        if (object instanceof THREE.Mesh) geometries.add(object.geometry);
        (Array.isArray(object.material) ? object.material : [object.material]).forEach(material => materials.add(material));
      });
      geometries.forEach(geometry => geometry.dispose());
      const textures = new Set<THREE.Texture>();
      materials.forEach(material => {
        const map = (material as THREE.MeshBasicMaterial).map;
        if (map) textures.add(map);
        material.dispose();
      });
      textures.forEach(texture => texture.dispose());
      environment?.dispose();
      renderer.dispose();
    };
    if (compilation) compilation.then(release, release);
    else release();
  };
}
