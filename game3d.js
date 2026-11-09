// game3d.js - Shadows of Eldoria 3D Action Engine

// --- GAME STATE ---
const state = {
  hp: 100,
  maxHp: 100,
  mp: 60,
  maxMp: 60,
  xp: 0,
  xpNeeded: 100,
  level: 1,
  gold: 0,
  slain: 0,
  potions: 3,
  floor: 1,
  isPlaying: false,
  isLocked: false,
  isGameOver: false,
  isVictory: false,
};

// --- THREE.JS GLOBALS ---
let scene, camera, renderer, clock;
let dungeonGrid = [];
const MAP_SIZE = 21;
const TILE_SIZE = 4;
let dustMotes = null;

// Player physics & controls
const player = {
  pos: new THREE.Vector3(TILE_SIZE * 1.5, 1.6, TILE_SIZE * 1.5),
  vel: new THREE.Vector3(),
  yaw: 0,
  pitch: 0,
  speed: 9.0,
  jumpStrength: 8.0,
  canJump: false,
  radius: 0.6,
  height: 1.6,
  bobTimer: 0,
};

const keys = { KeyW: false, KeyA: false, KeyS: false, KeyD: false, Space: false };

// Combat & Viewmodel
let weaponMesh, weaponPivot;
let isSwinging = false;
let swingProgress = 0;
const projectiles = [];
const particles = [];
const enemies = [];
const chests = [];
let portal = null;
let torchLights = [];

// Wall collision boxes
const wallBoxes = [];

// --- INITIALIZATION ---
window.addEventListener('DOMContentLoaded', () => {
  initThree();
  initTexturesAndMaterials();
  generateDungeon(state.floor);
  setupControls();
  setupUI();
  animate();
});

function initThree() {
  const container = document.getElementById('game-container');
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0e111a);
  // Realistic atmospheric haze (preserves depth and contrast without blinding)
  scene.fog = new THREE.FogExp2(0x111420, 0.022);

  camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.copy(player.pos);

  renderer = new THREE.WebGLRenderer({ antialias: false, powerPreference: 'high-performance' });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(1.0); // 1.0 Pixel Ratio for silky smooth 60 FPS
  renderer.shadowMap.enabled = false; // Disable heavy shadow maps to eliminate GPU lag
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.3;
  container.appendChild(renderer.domElement);

  clock = new THREE.Clock();

  // Optimized PBR Lighting setup
  const ambientLight = new THREE.AmbientLight(0x333b4e, 1.2);
  scene.add(ambientLight);

  const hemiLight = new THREE.HemisphereLight(0x4a6080, 0x241d16, 0.85);
  scene.add(hemiLight);

  // Player personal warm brass lantern
  const playerLight = new THREE.PointLight(0xffeed8, 2.2, 25, 1.2);
  playerLight.position.set(0, 0.2, 0);
  camera.add(playerLight);

  // Forward lantern beam illuminating path ahead
  const playerSpot = new THREE.SpotLight(0xffe6c2, 2.0, 32, Math.PI / 3.4, 0.4, 1.2);
  playerSpot.position.set(0, 0, 0);
  playerSpot.target.position.set(0, 0, -10);
  camera.add(playerSpot);
  camera.add(playerSpot.target);

  scene.add(camera);

  // Lightweight ambient dust motes (GPU instanced points)
  const moteGeo = new THREE.BufferGeometry();
  const moteCount = 60;
  const motePositions = new Float32Array(moteCount * 3);
  for (let i = 0; i < moteCount * 3; i += 3) {
    motePositions[i] = (Math.random() - 0.5) * 32;
    motePositions[i + 1] = Math.random() * 3.2;
    motePositions[i + 2] = (Math.random() - 0.5) * 32;
  }
  moteGeo.setAttribute('position', new THREE.BufferAttribute(motePositions, 3));
  const moteMat = new THREE.PointsMaterial({
    color: 0xffd59e,
    size: 0.05,
    transparent: true,
    opacity: 0.6,
  });
  dustMotes = new THREE.Points(moteGeo, moteMat);
  scene.add(dustMotes);

  // Build First-Person Viewmodel (Sword)
  buildWeaponViewmodel();

  window.addEventListener('resize', onWindowResize);
}

// Procedural Canvas Textures
let stoneMat, floorMat, ceilingMat, metalMat, goldMat;

function initTexturesAndMaterials() {
  // 1. Realistic Medieval Stone Wall (512x512 with Diffuse, Bump & Roughness Maps)
  const stoneW = 512, stoneH = 512;
  const sCanvas = document.createElement('canvas');
  sCanvas.width = stoneW; sCanvas.height = stoneH;
  const sCtx = sCanvas.getContext('2d');

  const bCanvas = document.createElement('canvas');
  bCanvas.width = stoneW; bCanvas.height = stoneH;
  const bCtx = bCanvas.getContext('2d');

  const rCanvas = document.createElement('canvas');
  rCanvas.width = stoneW; rCanvas.height = stoneH;
  const rCtx = rCanvas.getContext('2d');

  // Base Mortar (dark aged mortar)
  sCtx.fillStyle = '#1c1a17';
  sCtx.fillRect(0, 0, stoneW, stoneH);
  bCtx.fillStyle = '#121212';
  bCtx.fillRect(0, 0, stoneW, stoneH);
  rCtx.fillStyle = '#f0f0f0';
  rCtx.fillRect(0, 0, stoneW, stoneH);

  const rows = 8;
  const rowH = stoneH / rows;

  for (let r = 0; r < rows; r++) {
    const y = r * rowH;
    const shift = (r % 2 === 0) ? 0 : 38;
    const blockW = 85;

    for (let x = -shift; x < stoneW + 85; x += blockW) {
      const bw = blockW - 5;
      const bh = rowH - 5;

      // Authentic ancient limestone / granite hues
      const stoneHues = [
        [78, 72, 65],   // warm weathered limestone
        [68, 64, 59],   // aged ashlar stone
        [62, 59, 55],   // cool dark granite
        [85, 78, 70],   // chiseled highlight block
        [56, 52, 47],   // dark mineral block
      ];
      const baseRgb = stoneHues[Math.floor(Math.random() * stoneHues.length)];

      // Diffuse gradient bevel
      const grad = sCtx.createLinearGradient(x, y, x + bw, y + bh);
      grad.addColorStop(0, `rgb(${baseRgb[0] + 16}, ${baseRgb[1] + 15}, ${baseRgb[2] + 14})`);
      grad.addColorStop(0.5, `rgb(${baseRgb[0]}, ${baseRgb[1]}, ${baseRgb[2]})`);
      grad.addColorStop(1, `rgb(${baseRgb[0] - 14}, ${baseRgb[1] - 14}, ${baseRgb[2] - 13})`);

      sCtx.fillStyle = grad;
      sCtx.fillRect(x + 2, y + 2, bw, bh);

      // Bump map bevel (raised stone face with softened edges)
      const bGrad = bCtx.createRadialGradient(x + bw/2, y + bh/2, 2, x + bw/2, y + bh/2, Math.max(bw, bh)/1.3);
      bGrad.addColorStop(0, '#e5e5e5');
      bGrad.addColorStop(0.8, '#999999');
      bGrad.addColorStop(1, '#333333');
      bCtx.fillStyle = bGrad;
      bCtx.fillRect(x + 2, y + 2, bw, bh);

      // Roughness map (tactile stone matte finish)
      rCtx.fillStyle = '#b5b5b5';
      rCtx.fillRect(x + 2, y + 2, bw, bh);
    }
  }

  // Add realistic micro-grain noise and porous stone grit
  const sImgData = sCtx.getImageData(0, 0, stoneW, stoneH);
  const bImgData = bCtx.getImageData(0, 0, stoneW, stoneH);
  const rImgData = rCtx.getImageData(0, 0, stoneW, stoneH);
  const sData = sImgData.data;
  const bData = bImgData.data;
  const rData = rImgData.data;

  for (let i = 0; i < sData.length; i += 4) {
    const noise = (Math.random() - 0.5) * 22;
    sData[i] = Math.max(0, Math.min(255, sData[i] + noise));
    sData[i + 1] = Math.max(0, Math.min(255, sData[i + 1] + noise));
    sData[i + 2] = Math.max(0, Math.min(255, sData[i + 2] + noise));

    bData[i] = Math.max(0, Math.min(255, bData[i] + noise * 1.5));
    bData[i + 1] = bData[i];
    bData[i + 2] = bData[i];

    rData[i] = Math.max(0, Math.min(255, rData[i] + (Math.random() - 0.5) * 20));
    rData[i + 1] = rData[i];
    rData[i + 2] = rData[i];
  }
  sCtx.putImageData(sImgData, 0, 0);
  bCtx.putImageData(bImgData, 0, 0);
  rCtx.putImageData(rImgData, 0, 0);

  const stoneTex = new THREE.CanvasTexture(sCanvas);
  stoneTex.wrapS = THREE.RepeatWrapping;
  stoneTex.wrapT = THREE.RepeatWrapping;
  stoneTex.repeat.set(1, 1);

  const stoneBumpTex = new THREE.CanvasTexture(bCanvas);
  stoneBumpTex.wrapS = THREE.RepeatWrapping;
  stoneBumpTex.wrapT = THREE.RepeatWrapping;
  stoneBumpTex.repeat.set(1, 1);

  const stoneRoughTex = new THREE.CanvasTexture(rCanvas);
  stoneRoughTex.wrapS = THREE.RepeatWrapping;
  stoneRoughTex.wrapT = THREE.RepeatWrapping;
  stoneRoughTex.repeat.set(1, 1);

  stoneMat = new THREE.MeshStandardMaterial({
    map: stoneTex,
    bumpMap: stoneBumpTex,
    bumpScale: 0.12,
    roughnessMap: stoneRoughTex,
    roughness: 0.78,
    metalness: 0.08,
  });

  // 2. Realistic Flagstone Pavement with Wet Reflective Puddles (512x512)
  const fCanvas = document.createElement('canvas');
  fCanvas.width = 512; fCanvas.height = 512;
  const fCtx = fCanvas.getContext('2d');

  const fbCanvas = document.createElement('canvas');
  fbCanvas.width = 512; fbCanvas.height = 512;
  const fbCtx = fbCanvas.getContext('2d');

  const frCanvas = document.createElement('canvas');
  frCanvas.width = 512; frCanvas.height = 512;
  const frCtx = frCanvas.getContext('2d');

  // Dark joint lines
  fCtx.fillStyle = '#17181c';
  fCtx.fillRect(0, 0, 512, 512);
  fbCtx.fillStyle = '#080808';
  fbCtx.fillRect(0, 0, 512, 512);
  frCtx.fillStyle = '#d5d5d5';
  frCtx.fillRect(0, 0, 512, 512);

  const tileSize = 64;
  for (let y = 0; y < 512; y += tileSize) {
    for (let x = 0; x < 512; x += tileSize) {
      const fw = tileSize - 4;
      const fh = tileSize - 4;

      const slateHues = [
        [52, 55, 62],
        [46, 48, 55],
        [58, 62, 70],
        [42, 44, 49],
        [50, 52, 58],
      ];
      const baseCol = slateHues[Math.floor(Math.random() * slateHues.length)];

      const grad = fCtx.createLinearGradient(x, y, x + fw, y + fh);
      grad.addColorStop(0, `rgb(${baseCol[0] + 12}, ${baseCol[1] + 12}, ${baseCol[2] + 14})`);
      grad.addColorStop(1, `rgb(${baseCol[0] - 8}, ${baseCol[1] - 8}, ${baseCol[2] - 10})`);
      fCtx.fillStyle = grad;
      fCtx.fillRect(x + 2, y + 2, fw, fh);

      const bGrad = fbCtx.createRadialGradient(x + fw/2, y + fh/2, 2, x + fw/2, y + fh/2, fw/1.4);
      bGrad.addColorStop(0, '#dcdcdc');
      bGrad.addColorStop(0.8, '#888888');
      bGrad.addColorStop(1, '#252525');
      fbCtx.fillStyle = bGrad;
      fbCtx.fillRect(x + 2, y + 2, fw, fh);

      frCtx.fillStyle = '#b8b8b8';
      frCtx.fillRect(x + 2, y + 2, fw, fh);
    }
  }

  // Realistic damp reflective water puddles!
  const puddles = [
    { x: 130, y: 160, rx: 70, ry: 45 },
    { x: 380, y: 310, rx: 80, ry: 50 },
    { x: 260, y: 430, rx: 55, ry: 35 },
  ];

  for (const pud of puddles) {
    const pGrad = fCtx.createRadialGradient(pud.x, pud.y, 4, pud.x, pud.y, pud.rx);
    pGrad.addColorStop(0, 'rgba(18, 20, 26, 0.88)');
    pGrad.addColorStop(0.7, 'rgba(25, 27, 34, 0.55)');
    pGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');
    fCtx.fillStyle = pGrad;
    fCtx.beginPath();
    fCtx.ellipse(pud.x, pud.y, pud.rx, pud.ry, 0, 0, Math.PI * 2);
    fCtx.fill();

    fbCtx.fillStyle = '#999999';
    fbCtx.beginPath();
    fbCtx.ellipse(pud.x, pud.y, pud.rx * 0.9, pud.ry * 0.9, 0, 0, Math.PI * 2);
    fbCtx.fill();

    // High specular gloss for water puddle reflections
    const rGrad = frCtx.createRadialGradient(pud.x, pud.y, 4, pud.x, pud.y, pud.rx);
    rGrad.addColorStop(0, '#1c1c1c'); // mirror-like water reflection
    rGrad.addColorStop(0.8, '#353535');
    rGrad.addColorStop(1, '#b8b8b8');
    frCtx.fillStyle = rGrad;
    frCtx.beginPath();
    frCtx.ellipse(pud.x, pud.y, pud.rx, pud.ry, 0, 0, Math.PI * 2);
    frCtx.fill();
  }

  const floorTex = new THREE.CanvasTexture(fCanvas);
  floorTex.wrapS = THREE.RepeatWrapping;
  floorTex.wrapT = THREE.RepeatWrapping;
  floorTex.repeat.set(MAP_SIZE, MAP_SIZE);

  const floorBumpTex = new THREE.CanvasTexture(fbCanvas);
  floorBumpTex.wrapS = THREE.RepeatWrapping;
  floorBumpTex.wrapT = THREE.RepeatWrapping;
  floorBumpTex.repeat.set(MAP_SIZE, MAP_SIZE);

  const floorRoughTex = new THREE.CanvasTexture(frCanvas);
  floorRoughTex.wrapS = THREE.RepeatWrapping;
  floorRoughTex.wrapT = THREE.RepeatWrapping;
  floorRoughTex.repeat.set(MAP_SIZE, MAP_SIZE);

  floorMat = new THREE.MeshStandardMaterial({
    map: floorTex,
    bumpMap: floorBumpTex,
    bumpScale: 0.1,
    roughnessMap: floorRoughTex,
    roughness: 0.65,
    metalness: 0.18,
  });

  // 3. Ancient Heavy Dark Timber Oak Ceiling (512x512)
  const cCanvas = document.createElement('canvas');
  cCanvas.width = 512; cCanvas.height = 512;
  const cCtx = cCanvas.getContext('2d');

  cCtx.fillStyle = '#261c14'; // Dark bog oak
  cCtx.fillRect(0, 0, 512, 512);

  for (let i = 0; i < 512; i += 32) {
    cCtx.fillStyle = (i % 64 === 0) ? '#1e150d' : '#2b2016';
    cCtx.fillRect(0, i, 512, 30);

    for (let g = 0; g < 4; g++) {
      cCtx.fillStyle = 'rgba(15, 10, 6, 0.35)';
      cCtx.fillRect(0, i + g * 7, 512, 1.5);
    }
  }

  cCtx.fillStyle = '#181109';
  cCtx.fillRect(100, 0, 50, 512);
  cCtx.fillRect(360, 0, 50, 512);

  cCtx.fillStyle = '#3a3a3a';
  for (let y = 30; y < 512; y += 60) {
    cCtx.beginPath(); cCtx.arc(125, y, 4, 0, Math.PI * 2); cCtx.fill();
    cCtx.beginPath(); cCtx.arc(385, y, 4, 0, Math.PI * 2); cCtx.fill();
  }

  const ceilingTex = new THREE.CanvasTexture(cCanvas);
  ceilingTex.wrapS = THREE.RepeatWrapping;
  ceilingTex.wrapT = THREE.RepeatWrapping;
  ceilingTex.repeat.set(MAP_SIZE / 2, MAP_SIZE / 2);

  ceilingMat = new THREE.MeshStandardMaterial({
    map: ceilingTex,
    roughness: 0.88,
    metalness: 0.05,
  });

  metalMat = new THREE.MeshStandardMaterial({
    color: 0xdce2ea, // Hand-forged knight's steel
    roughness: 0.22,
    metalness: 0.95,
  });

  goldMat = new THREE.MeshStandardMaterial({
    color: 0xc89b3c, // Antiqued engraved brass/gold
    roughness: 0.28,
    metalness: 0.88,
  });
}

// --- DUNGEON GENERATOR ---
function generateDungeon(floorLevel) {
  // Clear old world meshes
  clearWorld();

  // 1 = Wall, 0 = Empty Corridor / Room
  dungeonGrid = Array(MAP_SIZE).fill(0).map(() => Array(MAP_SIZE).fill(1));

  // Carve Rooms and Corridors (Simple BSP/Room placer)
  const rooms = [];
  const numRooms = 8;
  for (let i = 0; i < numRooms; i++) {
    const w = Math.floor(Math.random() * 3) + 3; // 3 to 5
    const h = Math.floor(Math.random() * 3) + 3;
    const x = Math.floor(Math.random() * (MAP_SIZE - w - 2)) + 1;
    const y = Math.floor(Math.random() * (MAP_SIZE - h - 2)) + 1;

    for (let ry = y; ry < y + h; ry++) {
      for (let rx = x; rx < x + w; rx++) {
        dungeonGrid[ry][rx] = 0;
      }
    }
    rooms.push({ x: Math.floor(x + w / 2), y: Math.floor(y + h / 2) });
  }

  // Connect rooms with corridors
  for (let i = 0; i < rooms.length - 1; i++) {
    const rA = rooms[i];
    const rB = rooms[i + 1];

    let cx = rA.x;
    let cy = rA.y;
    while (cx !== rB.x) {
      dungeonGrid[cy][cx] = 0;
      cx += cx < rB.x ? 1 : -1;
    }
    while (cy !== rB.y) {
      dungeonGrid[cy][cx] = 0;
      cy += cy < rB.y ? 1 : -1;
    }
  }

  // Set Player Start Position in Room 0
  const startRoom = rooms[0];
  player.pos.set(startRoom.x * TILE_SIZE + TILE_SIZE / 2, 1.6, startRoom.y * TILE_SIZE + TILE_SIZE / 2);
  camera.position.copy(player.pos);

  // Build Floor and Ceiling
  const floorGeo = new THREE.PlaneGeometry(MAP_SIZE * TILE_SIZE, MAP_SIZE * TILE_SIZE);
  const floorMesh = new THREE.Mesh(floorGeo, floorMat);
  floorMesh.rotation.x = -Math.PI / 2;
  floorMesh.position.set((MAP_SIZE * TILE_SIZE) / 2, 0, (MAP_SIZE * TILE_SIZE) / 2);
  floorMesh.receiveShadow = true;
  scene.add(floorMesh);

  const ceilingMesh = new THREE.Mesh(floorGeo, ceilingMat);
  ceilingMesh.rotation.x = Math.PI / 2;
  ceilingMesh.position.set((MAP_SIZE * TILE_SIZE) / 2, 4.2, (MAP_SIZE * TILE_SIZE) / 2);
  scene.add(ceilingMesh);

  // Count total walls for ultra-fast GPU InstancedMesh (1 Draw Call!)
  let wallCount = 0;
  for (let z = 0; z < MAP_SIZE; z++) {
    for (let x = 0; x < MAP_SIZE; x++) {
      if (dungeonGrid[z][x] === 1) wallCount++;
    }
  }

  const wallGeo = new THREE.BoxGeometry(TILE_SIZE, 4.2, TILE_SIZE);
  const wallInstanced = new THREE.InstancedMesh(wallGeo, stoneMat, wallCount);
  const dummy = new THREE.Object3D();

  let wallIdx = 0;
  for (let z = 0; z < MAP_SIZE; z++) {
    for (let x = 0; x < MAP_SIZE; x++) {
      if (dungeonGrid[z][x] === 1) {
        dummy.position.set(x * TILE_SIZE + TILE_SIZE / 2, 2.1, z * TILE_SIZE + TILE_SIZE / 2);
        dummy.updateMatrix();
        wallInstanced.setMatrixAt(wallIdx++, dummy.matrix);
      }
    }
  }
  wallInstanced.instanceMatrix.needsUpdate = true;
  scene.add(wallInstanced);

  // Balanced light budget: spawn Torches only in select rooms (max 4 dynamic point lights)
  for (let i = 0; i < rooms.length; i += 2) {
    const r = rooms[i];
    spawnTorch(r.x * TILE_SIZE + 1.2, 2.2, r.y * TILE_SIZE + 1.2, true);
  }

  // Spawn Portal in Last Room
  const endRoom = rooms[rooms.length - 1];
  spawnPortal(endRoom.x * TILE_SIZE + TILE_SIZE / 2, endRoom.y * TILE_SIZE + TILE_SIZE / 2);

  // Spawn Enemies in intermediary rooms
  for (let i = 1; i < rooms.length; i++) {
    const r = rooms[i];
    const isBossRoom = (i === rooms.length - 1 && floorLevel === 3);
    const count = isBossRoom ? 1 : Math.floor(Math.random() * 2) + 1;

    for (let c = 0; c < count; c++) {
      const offsetX = (Math.random() - 0.5) * 2;
      const offsetZ = (Math.random() - 0.5) * 2;
      const ex = r.x * TILE_SIZE + TILE_SIZE / 2 + offsetX;
      const ez = r.y * TILE_SIZE + TILE_SIZE / 2 + offsetZ;

      if (isBossRoom) {
        spawnEnemy(ex, ez, 'boss');
      } else if (floorLevel >= 2 && Math.random() < 0.45) {
        spawnEnemy(ex, ez, 'skeleton');
      } else {
        spawnEnemy(ex, ez, 'goblin');
      }
    }

    // Spawn Chests in select rooms
    if (Math.random() < 0.45 && !isBossRoom) {
      spawnChest(r.x * TILE_SIZE + TILE_SIZE / 2 + 1.5, r.y * TILE_SIZE + TILE_SIZE / 2);
    }
  }

  updateHUD();
}

function clearWorld() {
  wallBoxes.length = 0;
  torchLights.length = 0;
  for (const e of enemies) {
    if (e.mesh) scene.remove(e.mesh);
  }
  enemies.length = 0;
  for (const c of chests) {
    if (c.mesh) scene.remove(c.mesh);
  }
  chests.length = 0;
  if (portal && portal.mesh) scene.remove(portal.mesh);
  portal = null;

  // Remove walls, floors, torches from scene
  const toRemove = [];
  scene.traverse((obj) => {
    if (obj !== camera && !camera.children.includes(obj) && obj.type === 'Mesh') {
      toRemove.push(obj);
    }
    if (obj.type === 'PointLight' && obj.parent !== camera) {
      toRemove.push(obj);
    }
  });
  toRemove.forEach((o) => scene.remove(o));
}

// --- WEAPON VIEWMODEL ---
function buildWeaponViewmodel() {
  weaponPivot = new THREE.Group();
  weaponPivot.position.set(0.36, -0.30, -0.55);

  weaponMesh = new THREE.Group();

  // Polished Damascus Steel Blade
  const bladeGeo = new THREE.BoxGeometry(0.055, 0.82, 0.016);
  const bladeMat = new THREE.MeshStandardMaterial({
    color: 0xecf0f5,
    roughness: 0.16,
    metalness: 0.98,
  });
  const bladeMesh = new THREE.Mesh(bladeGeo, bladeMat);
  bladeMesh.position.set(0, 0.48, 0);
  weaponMesh.add(bladeMesh);

  // Central Fuller (Blood Groove)
  const fullerGeo = new THREE.BoxGeometry(0.016, 0.72, 0.018);
  const fullerMat = new THREE.MeshStandardMaterial({
    color: 0x475569,
    roughness: 0.35,
    metalness: 0.9,
  });
  const fullerMesh = new THREE.Mesh(fullerGeo, fullerMat);
  fullerMesh.position.set(0, 0.46, 0);
  weaponMesh.add(fullerMesh);

  // Antiqued Curved Bronze Crossguard
  const guardGeo = new THREE.BoxGeometry(0.26, 0.045, 0.045);
  const guardMat = new THREE.MeshStandardMaterial({
    color: 0xb48238, // forged bronze
    roughness: 0.32,
    metalness: 0.85,
  });
  const guardMesh = new THREE.Mesh(guardGeo, guardMat);
  guardMesh.position.set(0, 0.07, 0);
  weaponMesh.add(guardMesh);

  // Crossguard Quillon Finials
  const finialGeo = new THREE.SphereGeometry(0.026, 8, 8);
  const fL = new THREE.Mesh(finialGeo, guardMat);
  fL.position.set(-0.13, 0.07, 0);
  const fR = new THREE.Mesh(finialGeo, guardMat);
  fR.position.set(0.13, 0.07, 0);
  weaponMesh.add(fL);
  weaponMesh.add(fR);

  // Wrapped Dark Leather Grip
  const gripGeo = new THREE.CylinderGeometry(0.024, 0.026, 0.18, 10);
  const gripMat = new THREE.MeshStandardMaterial({
    color: 0x2e1a0e, // dark oiled brown leather
    roughness: 0.82,
  });
  const gripMesh = new THREE.Mesh(gripGeo, gripMat);
  gripMesh.position.set(0, -0.04, 0);
  weaponMesh.add(gripMesh);

  // Faceted Ringed Pommel
  const pommelGeo = new THREE.CylinderGeometry(0.038, 0.038, 0.03, 8);
  const pommelMesh = new THREE.Mesh(pommelGeo, guardMat);
  pommelMesh.position.set(0, -0.14, 0);
  pommelMesh.rotation.x = Math.PI / 2;
  weaponMesh.add(pommelMesh);

  // Subtle tilt for first-person perspective
  weaponMesh.rotation.x = 0.22;
  weaponMesh.rotation.y = -0.14;
  weaponMesh.rotation.z = -0.12;

  weaponPivot.add(weaponMesh);
  camera.add(weaponPivot);
}

// --- TORCHES & PARTICLES ---
function spawnTorch(x, y, z, hasLight = true) {
  const sconceGeo = new THREE.CylinderGeometry(0.06, 0.04, 0.5, 6);
  const sconceMat = new THREE.MeshStandardMaterial({ color: 0x4e342e, roughness: 0.9 });
  const sconce = new THREE.Mesh(sconceGeo, sconceMat);
  sconce.position.set(x, y, z);
  scene.add(sconce);

  const flameGeo = new THREE.DodecahedronGeometry(0.14);
  const flameMat = new THREE.MeshBasicMaterial({ color: 0xffd54f });
  const flame = new THREE.Mesh(flameGeo, flameMat);
  flame.position.set(x, y + 0.3, z);
  scene.add(flame);

  if (hasLight) {
    const light = new THREE.PointLight(0xffa040, 2.5, 14, 1.4);
    light.position.set(x, y + 0.35, z);
    scene.add(light);
    torchLights.push({ light, flame, baseIntensity: 2.5, seed: Math.random() * 100 });
  }
}

// --- PORTAL ---
function spawnPortal(x, z) {
  const portalGroup = new THREE.Group();
  portalGroup.position.set(x, 1.5, z);

  const ringGeo = new THREE.TorusGeometry(1.2, 0.15, 8, 24);
  const ringMat = new THREE.MeshStandardMaterial({ color: 0x581c87, roughness: 0.3, metalness: 0.8 });
  const ring = new THREE.Mesh(ringGeo, ringMat);
  portalGroup.add(ring);

  const discGeo = new THREE.CircleGeometry(1.05, 16);
  const discMat = new THREE.MeshBasicMaterial({ color: 0xa855f7, side: THREE.DoubleSide, transparent: true, opacity: 0.75 });
  const disc = new THREE.Mesh(discGeo, discMat);
  portalGroup.add(disc);

  const light = new THREE.PointLight(0xa855f7, 2.5, 12);
  portalGroup.add(light);

  scene.add(portalGroup);
  portal = { mesh: portalGroup, x, z };
}

// --- CHESTS ---
function spawnChest(x, z) {
  const chestGroup = new THREE.Group();
  chestGroup.position.set(x, 0.35, z);

  const boxGeo = new THREE.BoxGeometry(0.9, 0.6, 0.6);
  const boxMat = new THREE.MeshStandardMaterial({ color: 0x7c4a30, roughness: 0.7 });
  const chestBase = new THREE.Mesh(boxGeo, boxMat);
  chestBase.castShadow = true;
  chestGroup.add(chestBase);

  const lockGeo = new THREE.BoxGeometry(0.12, 0.12, 0.05);
  const lock = new THREE.Mesh(lockGeo, goldMat);
  lock.position.set(0, 0.08, 0.31);
  chestGroup.add(lock);

  // Subtle treasure glow
  const chestGlow = new THREE.PointLight(0xfacc15, 1.0, 4);
  chestGlow.position.set(0, 0.4, 0);
  chestGroup.add(chestGlow);

  scene.add(chestGroup);
  chests.push({ mesh: chestGroup, x, z, opened: false });
}

// --- 3D ENEMIES ---
function spawnEnemy(x, z, type) {
  const enemyGroup = new THREE.Group();
  enemyGroup.position.set(x, 0, z);

  let hp = 45;
  let maxHp = 45;
  let speed = 2.4;
  let atk = 10;
  let scale = 1.0;

  if (type === 'skeleton') {
    hp = 70;
    maxHp = 70;
    speed = 2.8;
    atk = 16;
    scale = 1.05;

    // Aged Bone Material
    const boneMat = new THREE.MeshStandardMaterial({
      color: 0xd4cbb8, // ancient calcium bone
      roughness: 0.85,
      metalness: 0.05,
    });

    // Ribcage & Spine
    const spineGeo = new THREE.CylinderGeometry(0.06, 0.06, 0.9, 6);
    const spine = new THREE.Mesh(spineGeo, boneMat);
    spine.position.y = 0.95;
    enemyGroup.add(spine);

    // Rib hoops
    for (let i = 0; i < 3; i++) {
      const ribGeo = new THREE.TorusGeometry(0.24 - i * 0.02, 0.025, 6, 12);
      const rib = new THREE.Mesh(ribGeo, boneMat);
      rib.position.y = 1.15 - i * 0.16;
      rib.rotation.x = Math.PI / 2;
      enemyGroup.add(rib);
    }

    // Skull
    const skullGeo = new THREE.SphereGeometry(0.22, 8, 8);
    const skull = new THREE.Mesh(skullGeo, boneMat);
    skull.position.y = 1.55;
    enemyGroup.add(skull);

    // Sunken Eerie Cyan Eye Embers
    const eyeGeo = new THREE.SphereGeometry(0.04, 6, 6);
    const eyeMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8 });
    const eyeL = new THREE.Mesh(eyeGeo, eyeMat);
    eyeL.position.set(-0.07, 1.56, 0.18);
    const eyeR = new THREE.Mesh(eyeGeo, eyeMat);
    eyeR.position.set(0.07, 1.56, 0.18);
    enemyGroup.add(eyeL);
    enemyGroup.add(eyeR);

    // Rusted Ancient Broadsword
    const wepMat = new THREE.MeshStandardMaterial({ color: 0x474b54, roughness: 0.65, metalness: 0.9 });
    const bladeGeo = new THREE.BoxGeometry(0.06, 0.65, 0.02);
    const blade = new THREE.Mesh(bladeGeo, wepMat);
    blade.position.set(0.35, 0.95, 0.2);
    blade.rotation.x = 0.6;
    enemyGroup.add(blade);

  } else if (type === 'boss') {
    hp = 260;
    maxHp = 260;
    speed = 2.2;
    atk = 28;
    scale = 1.85;

    // Dark Forged Obsidian Plate Armor
    const armorMat = new THREE.MeshStandardMaterial({
      color: 0x181a22,
      roughness: 0.32,
      metalness: 0.9,
    });

    const torsoGeo = new THREE.CylinderGeometry(0.38, 0.3, 0.95, 8);
    const torso = new THREE.Mesh(torsoGeo, armorMat);
    torso.position.y = 1.0 * scale;
    enemyGroup.add(torso);

    // Horned Helm
    const helmGeo = new THREE.DodecahedronGeometry(0.28 * scale);
    const helm = new THREE.Mesh(helmGeo, armorMat);
    helm.position.y = 1.65 * scale;
    enemyGroup.add(helm);

    // Horns
    const hornGeo = new THREE.ConeGeometry(0.08 * scale, 0.4 * scale, 6);
    const hornL = new THREE.Mesh(hornGeo, armorMat);
    hornL.position.set(-0.25 * scale, 1.85 * scale, 0);
    hornL.rotation.z = 0.6;
    const hornR = new THREE.Mesh(hornGeo, armorMat);
    hornR.position.set(0.25 * scale, 1.85 * scale, 0);
    hornR.rotation.z = -0.6;
    enemyGroup.add(hornL);
    enemyGroup.add(hornR);

    // Menacing Fiery Molten Eyes
    const eyeMat = new THREE.MeshBasicMaterial({ color: 0xf59e0b });
    const eyeL = new THREE.Mesh(new THREE.SphereGeometry(0.05 * scale, 6, 6), eyeMat);
    eyeL.position.set(-0.1 * scale, 1.68 * scale, 0.24 * scale);
    const eyeR = new THREE.Mesh(new THREE.SphereGeometry(0.05 * scale, 6, 6), eyeMat);
    eyeR.position.set(0.1 * scale, 1.68 * scale, 0.24 * scale);
    enemyGroup.add(eyeL);
    enemyGroup.add(eyeR);

    // Giant Flaming Demonic Claymore
    const swordMat = new THREE.MeshStandardMaterial({ color: 0xb91c1c, roughness: 0.25, metalness: 0.8 });
    const sword = new THREE.Mesh(new THREE.BoxGeometry(0.12 * scale, 1.1 * scale, 0.04 * scale), swordMat);
    sword.position.set(0.55 * scale, 1.1 * scale, 0.3 * scale);
    sword.rotation.x = 0.5;
    enemyGroup.add(sword);

  } else {
    // Goblin
    hp = 45;
    maxHp = 45;
    speed = 2.5;
    atk = 11;
    scale = 0.9;

    // Earthy Olive Hide
    const skinMat = new THREE.MeshStandardMaterial({
      color: 0x485c3b, // realistic mottled forest hide
      roughness: 0.75,
    });
    const leatherMat = new THREE.MeshStandardMaterial({
      color: 0x362417, // boiled leather armor vest
      roughness: 0.85,
    });

    const torso = new THREE.Mesh(new THREE.CylinderGeometry(0.26, 0.2, 0.7, 8), leatherMat);
    torso.position.y = 0.85;
    enemyGroup.add(torso);

    const head = new THREE.Mesh(new THREE.SphereGeometry(0.22, 8, 8), skinMat);
    head.position.y = 1.35;
    enemyGroup.add(head);

    // Pointed Goblin Ears
    const earGeo = new THREE.ConeGeometry(0.06, 0.25, 6);
    const earL = new THREE.Mesh(earGeo, skinMat);
    earL.position.set(-0.25, 1.4, 0);
    earL.rotation.z = 1.2;
    const earR = new THREE.Mesh(earGeo, skinMat);
    earR.position.set(0.25, 1.4, 0);
    earR.rotation.z = -1.2;
    enemyGroup.add(earL);
    enemyGroup.add(earR);

    // Amber Slit Eyes
    const eyeMat = new THREE.MeshBasicMaterial({ color: 0xeab308 });
    const eyeL = new THREE.Mesh(new THREE.SphereGeometry(0.04, 6, 6), eyeMat);
    eyeL.position.set(-0.07, 1.38, 0.2);
    const eyeR = new THREE.Mesh(new THREE.SphereGeometry(0.04, 6, 6), eyeMat);
    eyeR.position.set(0.07, 1.38, 0.2);
    enemyGroup.add(eyeL);
    enemyGroup.add(eyeR);

    // Heavy Spiked Wooden Club
    const clubMat = new THREE.MeshStandardMaterial({ color: 0x3d2b1f, roughness: 0.8 });
    const club = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.08, 0.65, 8), clubMat);
    club.position.set(0.35, 0.85, 0.2);
    club.rotation.x = 0.5;
    enemyGroup.add(club);
  }

  // Floating 3D Overhead Health Bar Billboard
  const hpGroup = new THREE.Group();
  hpGroup.position.y = 2.1 * scale;

  const hpBgGeo = new THREE.PlaneGeometry(0.8 * scale, 0.12 * scale);
  const hpBgMat = new THREE.MeshBasicMaterial({ color: 0x0f172a, side: THREE.DoubleSide });
  const hpBg = new THREE.Mesh(hpBgGeo, hpBgMat);
  hpGroup.add(hpBg);

  const hpFillGeo = new THREE.PlaneGeometry(0.76 * scale, 0.08 * scale);
  const hpFillMat = new THREE.MeshBasicMaterial({ color: 0xef4444, side: THREE.DoubleSide });
  const hpFill = new THREE.Mesh(hpFillGeo, hpFillMat);
  hpFill.position.set(0, 0, 0.01);
  hpGroup.add(hpFill);

  enemyGroup.add(hpGroup);

  scene.add(enemyGroup);

  enemies.push({
    mesh: enemyGroup,
    hpGroup,
    hpFill,
    type,
    hp,
    maxHp,
    speed,
    atk,
    scale,
    lastAttack: 0,
    hurtTimer: 0,
    isDead: false,
  });
}

// --- PLAYER CONTROLS & POINTER LOCK ---
function setupControls() {
  const blocker = document.getElementById('blocker');
  const startBtn = document.getElementById('start-btn');

  startBtn.addEventListener('click', () => {
    try {
      sounds.init();
    } catch (e) {}
    state.isPlaying = true;
    blocker.classList.add('hidden');
    try {
      document.body.requestPointerLock();
    } catch (e) {}
  });

  // Re-acquire pointer lock on canvas click if playing
  document.addEventListener('click', (e) => {
    if (state.isPlaying && !state.isLocked && !state.isGameOver && !state.isVictory) {
      if (!e.target.closest('#instructions') && !e.target.closest('.modal-card')) {
        try {
          document.body.requestPointerLock();
        } catch (e) {}
      }
    }
  });

  document.addEventListener('pointerlockchange', () => {
    state.isLocked = (document.pointerLockElement === document.body);
    if (!state.isLocked && state.isPlaying && !state.isGameOver && !state.isVictory) {
      // Show paused blocker with resume text
      startBtn.innerText = "RESUME ADVENTURE (CLICK TO PLAY)";
      blocker.classList.remove('hidden');
    }
  });

  // Mouse look (supports both Pointer Lock and Drag-to-Look)
  let isDragging = false;

  window.addEventListener('mousedown', (e) => {
    if (!state.isPlaying) return;
    if (e.target.closest('#instructions') || e.target.closest('.modal-card')) return;

    isDragging = true;
    if (e.button === 0) slashSword();
    if (e.button === 2) castFireball();
  });

  window.addEventListener('mouseup', () => {
    isDragging = false;
  });

  document.addEventListener('mousemove', (e) => {
    if (!state.isPlaying) return;
    // Look around if locked or dragging
    if (!state.isLocked && !isDragging) return;

    const sens = 0.0024;
    player.yaw -= e.movementX * sens;
    player.pitch -= e.movementY * sens;

    // Clamp vertical look to -85 deg and +85 deg
    player.pitch = Math.max(-Math.PI / 2.1, Math.min(Math.PI / 2.1, player.pitch));
  });

  // Keyboard input (WASD, Arrows, Hotkeys)
  window.addEventListener('keydown', (e) => {
    if (e.code in keys) keys[e.code] = true;
    // Arrow keys fallback
    if (e.code === 'ArrowUp') keys.KeyW = true;
    if (e.code === 'ArrowDown') keys.KeyS = true;
    if (e.code === 'ArrowLeft') keys.KeyA = true;
    if (e.code === 'ArrowRight') keys.KeyD = true;

    if (e.code === 'KeyQ') drinkPotion();
    if (e.code === 'KeyE') castFireball();
    if (e.code === 'KeyF') checkInteractions();
  });

  window.addEventListener('keyup', (e) => {
    if (e.code in keys) keys[e.code] = false;
    if (e.code === 'ArrowUp') keys.KeyW = false;
    if (e.code === 'ArrowDown') keys.KeyS = false;
    if (e.code === 'ArrowLeft') keys.KeyA = false;
    if (e.code === 'ArrowRight') keys.KeyD = false;
  });

  // Prevent context menu on right click so spells can be cast
  window.addEventListener('contextmenu', (e) => e.preventDefault());
}

// --- COMBAT ACTIONS ---
function slashSword() {
  if (isSwinging) return;
  isSwinging = true;
  swingProgress = 0;
  sounds.playSwordSwing();

  // Raycast / proximity melee check
  const attackRange = 2.4;
  const forward = new THREE.Vector3(0, 0, -1).applyEuler(new THREE.Euler(0, player.yaw, 0));

  let hitAny = false;
  for (const enemy of enemies) {
    if (enemy.isDead) continue;
    const dist = player.pos.distanceTo(enemy.mesh.position);
    if (dist < attackRange) {
      const toEnemy = enemy.mesh.position.clone().sub(player.pos).normalize();
      const dot = forward.dot(toEnemy);
      if (dot > 0.4) {
        // Hit enemy!
        hitAny = true;
        const dmg = Math.floor(22 + Math.random() * 12);
        damageEnemy(enemy, dmg);
        spawnBloodSparks(enemy.mesh.position.clone().add(new THREE.Vector3(0, 1.0, 0)));
      }
    }
  }

  if (hitAny) {
    sounds.playHit();
  }
}

function castFireball() {
  const mpCost = 15;
  if (state.mp < mpCost) return;
  state.mp -= mpCost;
  updateHUD();

  sounds.playFireball();

  // Spawn projectile from player eye position
  const dir = new THREE.Vector3(0, 0, -1).applyEuler(new THREE.Euler(player.pitch, player.yaw, 0));
  const startPos = player.pos.clone().add(dir.clone().multiplyScalar(0.5));

  const fbGeo = new THREE.SphereGeometry(0.18, 8, 8);
  const fbMat = new THREE.MeshBasicMaterial({ color: 0xff6600 });
  const fbMesh = new THREE.Mesh(fbGeo, fbMat);
  fbMesh.position.copy(startPos);

  const fbLight = new THREE.PointLight(0xff4400, 2.5, 6);
  fbMesh.add(fbLight);

  scene.add(fbMesh);

  projectiles.push({
    mesh: fbMesh,
    dir: dir.normalize(),
    speed: 18.0,
    life: 2.5,
  });
}

function damageEnemy(enemy, amount) {
  enemy.hp -= amount;
  enemy.hurtTimer = 0.2;

  // Knockback
  const knockDir = enemy.mesh.position.clone().sub(player.pos).normalize();
  enemy.mesh.position.add(knockDir.multiplyScalar(0.4));

  if (enemy.hp <= 0 && !enemy.isDead) {
    enemy.isDead = true;
    state.slain += 1;
    state.gold += (enemy.type === 'boss' ? 120 : (enemy.type === 'skeleton' ? 35 : 18));
    state.xp += (enemy.type === 'boss' ? 100 : 35);

    if (state.xp >= state.xpNeeded) {
      state.xp -= state.xpNeeded;
      state.level += 1;
      state.maxHp += 20;
      state.hp = state.maxHp;
      state.maxMp += 15;
      state.mp = state.maxMp;
    }

    // Drop loot
    sounds.playCoin();
    spawnExplosionParticles(enemy.mesh.position, 0xfacc15, 20);

    // Fade out mesh
    scene.remove(enemy.mesh);
    updateHUD();

    if (enemy.type === 'boss') {
      setTimeout(showVictory, 1200);
    }
  }
}

function drinkPotion() {
  if (state.potions <= 0 || state.hp >= state.maxHp) return;
  state.potions -= 1;
  state.hp = Math.min(state.maxHp, state.hp + 50);
  sounds.playPotion();
  updateHUD();
}

function checkInteractions() {
  // Check Chests
  for (const c of chests) {
    if (c.opened) continue;
    const dist = player.pos.distanceTo(new THREE.Vector3(c.x, 1, c.z));
    if (dist < 2.5) {
      c.opened = true;
      c.mesh.rotation.x = -0.3; // Open lid
      state.gold += Math.floor(30 + Math.random() * 40);
      state.potions += 1;
      sounds.playChest();
      sounds.playCoin();
      spawnExplosionParticles(new THREE.Vector3(c.x, 1, c.z), 0xfacc15, 25);
      showInteractionToast("🎁 Chest opened! Found Gold & Health Potion!");
      updateHUD();
      return;
    }
  }

  // Check Portal
  if (portal) {
    const dist = player.pos.distanceTo(new THREE.Vector3(portal.x, 1, portal.z));
    if (dist < 2.5) {
      advanceFloor();
    }
  }
}

function advanceFloor() {
  if (state.floor < 3) {
    state.floor += 1;
    showInteractionToast(`🌀 Descending to Floor ${state.floor}!`);
    generateDungeon(state.floor);
  } else {
    showVictory();
  }
}

function takePlayerDamage(amount) {
  state.hp = Math.max(0, state.hp - amount);
  sounds.playPlayerHurt();
  flashDamageScreen();
  updateHUD();

  if (state.hp <= 0 && !state.isGameOver) {
    state.isGameOver = true;
    document.exitPointerLock();
    document.getElementById('end-slain').innerText = state.slain;
    document.getElementById('end-gold').innerText = state.gold;
    document.getElementById('game-over-screen').classList.remove('hidden');
  }
}

function flashDamageScreen() {
  const flash = document.getElementById('damage-flash');
  flash.style.opacity = '1';
  setTimeout(() => {
    flash.style.opacity = '0';
  }, 180);
}

// --- PARTICLES ---
function spawnBloodSparks(pos) {
  spawnExplosionParticles(pos, 0xdc2626, 15);
}

function spawnExplosionParticles(pos, colorHex, count) {
  for (let i = 0; i < count; i++) {
    const pGeo = new THREE.BoxGeometry(0.08, 0.08, 0.08);
    const pMat = new THREE.MeshBasicMaterial({ color: colorHex });
    const pMesh = new THREE.Mesh(pGeo, pMat);
    pMesh.position.copy(pos);

    const vel = new THREE.Vector3(
      (Math.random() - 0.5) * 4,
      Math.random() * 3 + 1,
      (Math.random() - 0.5) * 4
    );

    scene.add(pMesh);
    particles.push({ mesh: pMesh, vel, life: 0.6 });
  }
}

// --- MAIN LOOP & PHYSICS ---
function animate() {
  requestAnimationFrame(animate);

  const delta = Math.min(clock.getDelta(), 0.1);

  if (state.isPlaying && !state.isGameOver && !state.isVictory) {
    updatePlayerPhysics(delta);
    updateViewmodel(delta);
    updateEnemies(delta);
    updateProjectiles(delta);
    updateTorches(delta);
    updateParticles(delta);
    updatePortal(delta);
    checkProximityPrompts();

    // Drift floating atmospheric dust motes
    if (dustMotes) {
      dustMotes.position.copy(player.pos);
      dustMotes.rotation.y += delta * 0.04;
    }
  }

  renderMinimap();
  renderer.render(scene, camera);
}

function updatePlayerPhysics(delta) {
  // Convert WASD to local movement vector
  const moveDir = new THREE.Vector3();
  if (keys.KeyW) moveDir.z -= 1;
  if (keys.KeyS) moveDir.z += 1;
  if (keys.KeyA) moveDir.x -= 1;
  if (keys.KeyD) moveDir.x += 1;

  if (moveDir.lengthSq() > 0) {
    moveDir.normalize();
    moveDir.applyEuler(new THREE.Euler(0, player.yaw, 0));
    player.vel.x = moveDir.x * player.speed;
    player.vel.z = moveDir.z * player.speed;

    // Head bobbing
    player.bobTimer += delta * 10;
  } else {
    // Decelerate
    player.vel.x *= 0.75;
    player.vel.z *= 0.75;
  }

  // Gravity
  player.vel.y -= 20.0 * delta;

  // Jump
  if (keys.Space && player.canJump) {
    player.vel.y = player.jumpStrength;
    player.canJump = false;
  }

  // X Collision
  const nextX = player.pos.x + player.vel.x * delta;
  if (!checkWallCollision(nextX, player.pos.z)) {
    player.pos.x = nextX;
  } else {
    player.vel.x = 0;
  }

  // Z Collision
  const nextZ = player.pos.z + player.vel.z * delta;
  if (!checkWallCollision(player.pos.x, nextZ)) {
    player.pos.z = nextZ;
  } else {
    player.vel.z = 0;
  }

  // Y Collision (Floor & Ceiling)
  player.pos.y += player.vel.y * delta;
  if (player.pos.y <= player.height) {
    player.pos.y = player.height;
    player.vel.y = 0;
    player.canJump = true;
  } else if (player.pos.y >= 3.6) {
    player.pos.y = 3.6;
    player.vel.y = 0;
  }

  // Sync Camera position with subtle head bob
  const bobY = Math.sin(player.bobTimer) * 0.05;
  camera.position.set(player.pos.x, player.pos.y + bobY, player.pos.z);
  camera.rotation.set(player.pitch, player.yaw, 0, 'YXZ');

  // Regenerate Mana slowly
  if (state.mp < state.maxMp) {
    state.mp = Math.min(state.maxMp, state.mp + delta * 4);
    updateHUD();
  }
}

function checkWallCollision(x, z) {
  const minTileX = Math.floor((x - player.radius) / TILE_SIZE);
  const maxTileX = Math.floor((x + player.radius) / TILE_SIZE);
  const minTileZ = Math.floor((z - player.radius) / TILE_SIZE);
  const maxTileZ = Math.floor((z + player.radius) / TILE_SIZE);

  for (let tz = minTileZ; tz <= maxTileZ; tz++) {
    for (let tx = minTileX; tx <= maxTileX; tx++) {
      if (tz < 0 || tz >= MAP_SIZE || tx < 0 || tx >= MAP_SIZE) return true;
      if (dungeonGrid[tz][tx] === 1) return true;
    }
  }
  return false;
}

function updateViewmodel(delta) {
  if (!weaponMesh) return;

  // Sword Swing Animation
  if (isSwinging) {
    swingProgress += delta * 6.5;
    if (swingProgress <= 1.0) {
      const angle = Math.sin(swingProgress * Math.PI) * 1.3;
      weaponMesh.rotation.x = 0.25 - angle * 0.8;
      weaponMesh.rotation.y = -0.15 - angle * 0.9;
      weaponMesh.position.z = -angle * 0.2;
    } else {
      isSwinging = false;
      weaponMesh.rotation.set(0.25, -0.15, -0.15);
      weaponMesh.position.set(0, 0, 0);
    }
  } else {
    // Idle sway
    const sway = Math.sin(clock.getElapsedTime() * 2) * 0.015;
    weaponMesh.position.y = sway;
  }
}

function updateEnemies(delta) {
  const now = clock.getElapsedTime();

  for (const enemy of enemies) {
    if (enemy.isDead) continue;

    const dist = player.pos.distanceTo(enemy.mesh.position);

    // Keep overhead 3D health bar facing camera & update scale
    if (enemy.hpGroup) {
      enemy.hpGroup.quaternion.copy(camera.quaternion);
    }
    if (enemy.hpFill) {
      const healthRatio = Math.max(0.001, enemy.hp / enemy.maxHp);
      enemy.hpFill.scale.x = healthRatio;
    }

    // Hurt flash
    if (enemy.hurtTimer > 0) {
      enemy.hurtTimer -= delta;
      enemy.mesh.children[0].material.color.setHex(0xffffff);
    } else {
      enemy.mesh.children[0].material.color.setHex(
        enemy.type === 'boss' ? 0xe11d48 : (enemy.type === 'skeleton' ? 0xf8fafc : 0x22c55e)
      );
    }

    // AI: Chase player if within 14 units
    if (dist < 14.0 && dist > 1.2) {
      const toPlayer = player.pos.clone().sub(enemy.mesh.position);
      toPlayer.y = 0;
      toPlayer.normalize();

      const nextX = enemy.mesh.position.x + toPlayer.x * enemy.speed * delta;
      const nextZ = enemy.mesh.position.z + toPlayer.z * enemy.speed * delta;

      if (!checkWallCollision(nextX, enemy.mesh.position.z)) enemy.mesh.position.x = nextX;
      if (!checkWallCollision(enemy.mesh.position.x, nextZ)) enemy.mesh.position.z = nextZ;

      // Face player
      enemy.mesh.lookAt(player.pos.x, enemy.mesh.position.y, player.pos.z);
    }

    // Attack Player when close
    if (dist <= 1.6 && now - enemy.lastAttack > 1.4) {
      enemy.lastAttack = now;
      takePlayerDamage(enemy.atk);
    }
  }
}

function updateProjectiles(delta) {
  for (let i = projectiles.length - 1; i >= 0; i--) {
    const p = projectiles[i];
    p.life -= delta;

    const moveStep = p.dir.clone().multiplyScalar(p.speed * delta);
    p.mesh.position.add(moveStep);

    // Check hit wall
    if (checkWallCollision(p.mesh.position.x, p.mesh.position.z)) {
      triggerFireballExplosion(p.mesh.position);
      scene.remove(p.mesh);
      projectiles.splice(i, 1);
      continue;
    }

    // Check hit enemy
    let hit = false;
    for (const enemy of enemies) {
      if (enemy.isDead) continue;
      if (p.mesh.position.distanceTo(enemy.mesh.position.clone().add(new THREE.Vector3(0, 1, 0))) < 1.1) {
        hit = true;
        damageEnemy(enemy, Math.floor(45 + Math.random() * 20));
        break;
      }
    }

    if (hit || p.life <= 0) {
      triggerFireballExplosion(p.mesh.position);
      scene.remove(p.mesh);
      projectiles.splice(i, 1);
    }
  }
}

function triggerFireballExplosion(pos) {
  sounds.playExplosion();
  spawnExplosionParticles(pos, 0xff4400, 25);
  spawnExplosionParticles(pos, 0xfacc15, 15);

  // Splash damage
  const splashRadius = 3.5;
  for (const enemy of enemies) {
    if (enemy.isDead) continue;
    const d = pos.distanceTo(enemy.mesh.position);
    if (d < splashRadius) {
      const splashDmg = Math.floor(30 * (1 - d / splashRadius));
      damageEnemy(enemy, splashDmg);
    }
  }
}

function updateTorches(delta) {
  const time = clock.getElapsedTime();
  for (const t of torchLights) {
    const flicker = Math.sin(time * 12 + t.seed) * 0.25 + (Math.random() - 0.5) * 0.15;
    t.light.intensity = t.baseIntensity + flicker;
  }
}

function updateParticles(delta) {
  for (let i = particles.length - 1; i >= 0; i--) {
    const p = particles[i];
    p.life -= delta;
    p.vel.y -= 9.8 * delta;
    p.mesh.position.addScaledVector(p.vel, delta);

    if (p.life <= 0) {
      scene.remove(p.mesh);
      particles.splice(i, 1);
    }
  }
}

function updatePortal(delta) {
  if (portal && portal.mesh) {
    portal.mesh.children[0].rotation.z += delta * 1.5;
    portal.mesh.children[1].rotation.z -= delta * 1.0;
  }
}

// --- MINIMAP ---
function renderMinimap() {
  const canvas = document.getElementById('minimap');
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;

  ctx.fillStyle = '#0a0a14';
  ctx.fillRect(0, 0, w, h);

  const scale = w / (MAP_SIZE * TILE_SIZE);

  // Draw Walls & Corridors
  for (let z = 0; z < MAP_SIZE; z++) {
    for (let x = 0; x < MAP_SIZE; x++) {
      if (dungeonGrid[z][x] === 0) {
        ctx.fillStyle = '#1e1e38';
        ctx.fillRect(x * TILE_SIZE * scale, z * TILE_SIZE * scale, TILE_SIZE * scale, TILE_SIZE * scale);
      }
    }
  }

  // Draw Chests
  ctx.fillStyle = '#facc15';
  for (const c of chests) {
    if (!c.opened) {
      ctx.beginPath();
      ctx.arc(c.x * scale, c.z * scale, 2.5, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  // Draw Enemies
  ctx.fillStyle = '#ef4444';
  for (const e of enemies) {
    if (!e.isDead) {
      ctx.beginPath();
      ctx.arc(e.mesh.position.x * scale, e.mesh.position.z * scale, 3, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  // Draw Player Marker & View Direction
  const px = player.pos.x * scale;
  const pz = player.pos.z * scale;

  ctx.fillStyle = '#38bdf8';
  ctx.beginPath();
  ctx.arc(px, pz, 4, 0, Math.PI * 2);
  ctx.fill();

  ctx.strokeStyle = '#38bdf8';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(px, pz);
  ctx.lineTo(px - Math.sin(player.yaw) * 10, pz - Math.cos(player.yaw) * 10);
  ctx.stroke();
}

// --- HUD & PROMPTS ---
function updateHUD() {
  const hpPercent = Math.max(0, (state.hp / state.maxHp) * 100);
  const mpPercent = Math.max(0, (state.mp / state.maxMp) * 100);
  const xpPercent = Math.max(0, (state.xp / state.xpNeeded) * 100);

  document.getElementById('hp-bar').style.width = `${hpPercent}%`;
  document.getElementById('hp-text').innerText = `${Math.floor(state.hp)} / ${state.maxHp}`;

  document.getElementById('mp-bar').style.width = `${mpPercent}%`;
  document.getElementById('mp-text').innerText = `${Math.floor(state.mp)} / ${state.maxMp}`;

  document.getElementById('xp-bar').style.width = `${xpPercent}%`;
  document.getElementById('xp-text').innerText = `LVL ${state.level}`;

  document.getElementById('gold-value').innerText = state.gold;
  document.getElementById('slain-value').innerText = state.slain;
  document.getElementById('potion-count').innerText = state.potions;

  const floorNames = {
    1: '🏰 Floor 1: Crypt Entrance',
    2: '🕯️ Floor 2: Catacombs',
    3: '🌌 Floor 3: Void Sanctum',
  };
  document.getElementById('floor-badge').innerText = floorNames[state.floor] || `Floor ${state.floor}`;
}

function checkProximityPrompts() {
  const promptEl = document.getElementById('interaction-prompt');

  // Check Chests
  for (const c of chests) {
    if (!c.opened && player.pos.distanceTo(new THREE.Vector3(c.x, 1, c.z)) < 2.5) {
      promptEl.innerText = "Press [F] to Open Treasure Chest";
      promptEl.style.display = 'block';
      return;
    }
  }

  // Check Portal
  if (portal && player.pos.distanceTo(new THREE.Vector3(portal.x, 1, portal.z)) < 2.5) {
    promptEl.innerText = state.floor < 3 ? "Press [F] to Descend to Next Floor" : "Press [F] to Face Void Sovereign";
    promptEl.style.display = 'block';
    return;
  }

  promptEl.style.display = 'none';
}

function showInteractionToast(msg) {
  const promptEl = document.getElementById('interaction-prompt');
  promptEl.innerText = msg;
  promptEl.style.display = 'block';
  setTimeout(() => {
    promptEl.style.display = 'none';
  }, 2200);
}

function showVictory() {
  state.isVictory = true;
  document.exitPointerLock();
  document.getElementById('win-slain').innerText = state.slain;
  document.getElementById('win-gold').innerText = state.gold;
  document.getElementById('victory-screen').classList.remove('hidden');
}

function setupUI() {
  document.getElementById('restart-btn').addEventListener('click', () => {
    window.location.reload();
  });
  document.getElementById('win-btn').addEventListener('click', () => {
    window.location.reload();
  });
}

function onWindowResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(1.0);
}
