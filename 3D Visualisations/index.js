import * as THREE from 'three';

// Scene & Renderer setup
const scene = new THREE.Scene();
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
scene.background = new THREE.Color(0xffffff);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

let lastHoveredMesh = null;
let originalColor = null;

// Popup for hover
const popup = document.createElement('div');
popup.id = 'hoverPopup';
popup.style.position = 'absolute';
popup.style.background = 'rgba(0,0,0,0.7)';
popup.style.color = 'white';
popup.style.padding = '5px 10px';
popup.style.borderRadius = '4px';
popup.style.pointerEvents = 'none';
popup.style.display = 'none';
popup.style.fontFamily = 'sans-serif';
popup.style.fontSize = '12px';
popup.style.zIndex = 10;
popup.innerText = 'This is mesh';
document.body.appendChild(popup);

// Mouse move event for raycasting
window.addEventListener('mousemove', (event) => {
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);

    const meshesOnly = [];
    scene.traverse((child) => {
        if (child.isMesh && child.name) {
            meshesOnly.push(child);
        }
    });

    const intersects = raycaster.intersectObjects(meshesOnly, true);

    // Reset previous hovered mesh color only if different mesh hovered now
    if (
        lastHoveredMesh &&
        lastHoveredMesh !== intersects[0]?.object &&
        lastHoveredMesh.material &&
        originalColor !== null
    ) {
        lastHoveredMesh.material.color.setHex(originalColor);
        lastHoveredMesh = null;
        originalColor = null;
    }

    if (intersects.length > 0) {
        const hovered = intersects[0].object;

        if (hovered !== lastHoveredMesh && hovered.material?.color) {
            originalColor = hovered.material.color.getHex();
            hovered.material.color.set(0xffaa00); // Highlight color
            lastHoveredMesh = hovered;
        }

        popup.style.display = 'block';
        popup.style.left = `${event.clientX + 10}px`;
        popup.style.top = `${event.clientY + 10}px`;
        popup.innerText = `This is mesh: ${hovered.name}`;
    } else {
        popup.style.display = 'none';
    }
});

// Camera setup
const aspect = window.innerWidth / window.innerHeight;
const camera = new THREE.PerspectiveCamera(48, aspect, 0.1, 1000);
camera.position.set(-60, 50, 150);
camera.lookAt(0, 0, 0);

// Axes Helper
scene.add(new THREE.AxesHelper(100));

// Rod creation
function createRod(start, end) {
    const rodGroup = new THREE.Group();

    const width = 2;
    const height = 2;

    const startVec = new THREE.Vector3(...start);
    const endVec = new THREE.Vector3(...end);

    const length = startVec.distanceTo(endVec);
    const center = new THREE.Vector3().lerpVectors(startVec, endVec, 0.5);

    const geometry = new THREE.BoxGeometry(width, height, length);
    const material = new THREE.MeshBasicMaterial({ color: 0xffffff }).clone();
    const box = new THREE.Mesh(geometry, material);
    box.position.copy(center);
    box.lookAt(endVec);
    box.name = 'Rod';
    rodGroup.add(box);

    const edgeGeometry = new THREE.EdgesGeometry(geometry);
    const edgeMaterial = new THREE.LineBasicMaterial({ color: 0x000000, linewidth: 2 });
    const outline = new THREE.LineSegments(edgeGeometry, edgeMaterial);
    outline.position.copy(box.position);
    outline.rotation.copy(box.rotation);
    outline.name = 'Rod outline';
    rodGroup.add(outline);

    return rodGroup;
}

// Box creation
function createBox() {
    const boxGroup = new THREE.Group();
    const faceCoords = testModel.l3dModel.reflector.face;
    const topFace = faceCoords.map(([x, y, z]) => [x, y, z + 5]);

    function createFaceGeometry(vertices) {
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(vertices.length * 3);
        vertices.forEach((vertex, i) => {
            positions[i * 3] = vertex[0];
            positions[i * 3 + 1] = vertex[1];
            positions[i * 3 + 2] = vertex[2];
        });
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setIndex([0, 1, 2, 0, 2, 3]);
        return geometry;
    }

    const bottomFaceMesh = new THREE.Mesh(
        createFaceGeometry(faceCoords),
        new THREE.MeshBasicMaterial({ color: 0xffffff, side: THREE.DoubleSide }).clone()
    );
    bottomFaceMesh.name = 'Bottom face';
    boxGroup.add(bottomFaceMesh);

    const bottomEdges = new THREE.LineSegments(
        new THREE.EdgesGeometry(bottomFaceMesh.geometry),
        new THREE.LineBasicMaterial({ color: 0x000000, linewidth: 2 })
    );
    boxGroup.add(bottomEdges);

    const topFaceMesh = new THREE.Mesh(
        createFaceGeometry(topFace),
        new THREE.MeshBasicMaterial({ color: 0xffffff, side: THREE.DoubleSide }).clone()
    );
    topFaceMesh.name = 'Top face';
    boxGroup.add(topFaceMesh);

    const topEdges = new THREE.LineSegments(
        new THREE.EdgesGeometry(topFaceMesh.geometry),
        new THREE.LineBasicMaterial({ color: 0x000000, linewidth: 2 })
    );
    boxGroup.add(topEdges);

    for (let i = 0; i < 4; i++) {
        const next = (i + 1) % 4;
        const sideVertices = [
            faceCoords[i], faceCoords[next], topFace[next], topFace[i]
        ];

        const sideFaceMesh = new THREE.Mesh(
            createFaceGeometry(sideVertices),
            new THREE.MeshBasicMaterial({ color: 0xffffff, side: THREE.DoubleSide }).clone()
        );
        sideFaceMesh.name = `Side face ${i}`;
        boxGroup.add(sideFaceMesh);

        const sideEdges = new THREE.LineSegments(
            new THREE.EdgesGeometry(sideFaceMesh.geometry),
            new THREE.LineBasicMaterial({ color: 0x000000, linewidth: 2 })
        );
        boxGroup.add(sideEdges);
    }

    scene.add(boxGroup);
}

createBox();

// Create all rods
function createShape() {
    testModel.l3dModel.barList.forEach(bar => {
        const firstCoord = bar[0];
        const lastCoord = bar[bar.length - 1];
        console.log(`Adding rod with coords ${firstCoord} and ${lastCoord}`);
        scene.add(createRod(firstCoord, lastCoord));
    });
}

createShape();

// Camera animation setup
function setCameraToLookAtPoints() {
    const center = testModel.l3dModel.center;
    const max = testModel.l3dModel.max;
    const cameraDistance = 115;
    const theta = Math.PI * testModel.l3dModel.previewCameraAngle / 180;
    camera.position.set(
        center[0] + Math.cos(theta) * cameraDistance,
        center[1] + Math.sin(theta) * cameraDistance,
        max[2] - 120
    );
    camera.up.set(0, 0, 1);
    camera.lookAt(center[0], center[1], center[2]);
}

// Animate loop with requestAnimationFrame
function animate() {
    requestAnimationFrame(animate);
    setCameraToLookAtPoints();
    renderer.render(scene, camera);
    testModel.l3dModel.previewCameraAngle += 0.5;
}
animate();
