import * as THREE from 'three';

// Scene & Renderer setup
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffffff);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);


// Camera setup
const aspect = window.innerWidth / window.innerHeight;
const camera = new THREE.PerspectiveCamera(48, aspect, 0.1, 1000);
camera.position.set(-60, 50, 150);
camera.lookAt(0, 0, 0);

// Add Axes Helper
const axesHelper = new THREE.AxesHelper(100);
scene.add(axesHelper);

// Function to create lines
function createLine(p1, p2, color = 0x000000) {
    const material = new THREE.LineBasicMaterial({ color });
    const geometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(...p1),
        new THREE.Vector3(...p2)
    ]);
    const line = new THREE.Line(geometry, material);
    return line;
}

// Rod constants
const d = 2; // Distance from rod start/end to LED lamp
const p = 2; // Half thickness of rod
const h = 4; // Height of the rod
const scaleFactor = 2; // Scale factor to resize rod and components
const rodLength = 46 * scaleFactor; // Length of rod


function createRod(start, end) {
    const rodGroup = new THREE.Group();

    // Rod dimensions
    const width = 2; // Thickness
    const height = 2; // Height

    // Convert start and end into Vector3
    const startVec = new THREE.Vector3(...start);
    const endVec = new THREE.Vector3(...end);

    // Calculate length and center position
    const length = startVec.distanceTo(endVec);
    const center = new THREE.Vector3().lerpVectors(startVec, endVec, 0.5);

    // Create white mesh (solid part of the rod)
    const geometry = new THREE.BoxGeometry(width, height, length);
    const material = new THREE.MeshBasicMaterial({
        color: 0xffffff, // White color
    });

    const box = new THREE.Mesh(geometry, material);
    box.position.copy(center);
    box.lookAt(endVec);

    rodGroup.add(box);

    // Create the outline for the rod using the box's geometry
    const edgeGeometry = new THREE.EdgesGeometry(geometry); // Now using geometry of box directly
    const edgeMaterial = new THREE.LineBasicMaterial({
        color: 0x000000, // Color of the outline (black)
        linewidth: 2,    // Thickness of the outline
    });

    const outline = new THREE.LineSegments(edgeGeometry, edgeMaterial);
    outline.position.copy(box.position);
    outline.rotation.copy(box.rotation); // Ensure outline rotates with the rod

    rodGroup.add(outline);
    scene.add(rodGroup);
}

function createBox() {
    const boxGroup = new THREE.Group();
    const faceCoords = testModel.l3dModel.reflector.face;

    // Add 5 to the z-coordinate to create top face
    const topFace = faceCoords.map(([x, y, z]) => [x, y, z + 5]);

    // Function to create a mesh for a face using BufferGeometry
    function createFaceGeometry(vertices) {
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(vertices.length * 3); // 3 values per vertex (x, y, z)

        vertices.forEach((vertex, i) => {
            positions[i * 3] = vertex[0];
            positions[i * 3 + 1] = vertex[1];
            positions[i * 3 + 2] = vertex[2];
        });

        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

        // The face will always be a triangle, so we define two faces for each rectangle
        geometry.setIndex([0, 1, 2, 0, 2, 3]);

        return geometry;
    }

    // Create bottom face mesh
    const bottomFaceMesh = new THREE.Mesh(
        createFaceGeometry(faceCoords),
        new THREE.MeshBasicMaterial({ color: 0xffffff, side: THREE.DoubleSide, transparent: false, })
    );
    boxGroup.add(bottomFaceMesh);

    // Outline for bottom face
    const bottomEdgesGeometry = new THREE.EdgesGeometry(bottomFaceMesh.geometry);
    const bottomEdgesMaterial = new THREE.LineBasicMaterial({ color: 0x000000, linewidth: 2 });
    const bottomOutline = new THREE.LineSegments(bottomEdgesGeometry, bottomEdgesMaterial);
    boxGroup.add(bottomOutline);

    // Create top face mesh
    const topFaceMesh = new THREE.Mesh(
        createFaceGeometry(topFace),
        new THREE.MeshBasicMaterial({ color: 0xffffff, side: THREE.DoubleSide, transparent: false, })
    );
    boxGroup.add(topFaceMesh);

    // Outline for top face
    const topEdgesGeometry = new THREE.EdgesGeometry(topFaceMesh.geometry);
    const topEdgesMaterial = new THREE.LineBasicMaterial({ color: 0x000000, linewidth: 2 });
    const topOutline = new THREE.LineSegments(topEdgesGeometry, topEdgesMaterial);
    boxGroup.add(topOutline);

    // Create sides
    for (let i = 0; i < 4; i++) {
        const next = (i + 1) % 4;
        const sideVertices = [
            faceCoords[i], faceCoords[next], topFace[next], topFace[i]
        ];

        const sideFaceMesh = new THREE.Mesh(
            createFaceGeometry(sideVertices),
            new THREE.MeshBasicMaterial({ color: 0xffffff, side: THREE.DoubleSide, transparent: false, })
        );
        boxGroup.add(sideFaceMesh);

        // Outline for each side
        const sideEdgesGeometry = new THREE.EdgesGeometry(sideFaceMesh.geometry);
        const sideEdgesMaterial = new THREE.LineBasicMaterial({ color: 0x000000, linewidth: 2 });
        const sideOutline = new THREE.LineSegments(sideEdgesGeometry, sideEdgesMaterial);
        boxGroup.add(sideOutline);
    }

    // Add the box group to the scene
    scene.add(boxGroup);
}



createBox()


function createShape() {
    testModel.l3dModel.barList.forEach(bar => {
        const firstCoord = bar[0];
        const lastCoord = bar[bar.length - 1];
        console.log(`Adding rod with coords ${firstCoord} and ${lastCoord}`)
        scene.add(createRod(firstCoord, lastCoord));
    });}

    
    
    
    
    console.log(camera)
    // First rod (horizontal)
    /*
    const rod1 = createRod([-16.271806627419227, 1.6221377491229774, 29.64888542990047], [-18.69309561163186, -4.758760184794257, 25.565344353003578]);  // Create the first rod at (0, 0, 0)
    scene.add(rod1);  // Add the first rod to the scene
    scene.add(createRod([4.2065267105171475, 18.280792873810313, 10.601886437801241], [-1.7574584476490807, -26.936544899290503, 16.58713879225409]));
    scene.add(createRod([22.127627787141904, 6.402990295239248, 16.769069011254214], [-23.033220852129425, 1.998097815000114, 24.32517067933396]));
    scene.add(createRod([13.838379336415011, -18.865929744216242, 9.503188470683783], [-16.143768158789534, 10.386675409694256, 28.51255256539271]));
    const rod2 = createLine([10, 10, 0], [10,100,10]); 
    scene.add(rod2);*/



// Create two rods and make them form an X shape
createShape();

// Function to change camera view
function setCameraToLookAtPoints() {

    const center=testModel.l3dModel.center;
    const max=testModel.l3dModel.max;
    const cameraDistance=115;
    //const [cx,cy,cz]=center;
    //camera.up.set(0,0,1);
    const theta=Math.PI*testModel.l3dModel.previewCameraAngle/180;
    camera.position.set(
        center[0]+Math.cos(theta)*cameraDistance,
        center[1]+cameraDistance*Math.sin(theta),
        max[2]-120
    );
    

    camera.up.set(0,0,1);
    camera.lookAt(center[0],center[1],center[2]);

    
    //camera.position.set(a.x + cameraDistance, a.y + cameraDistance / 2, a.z + cameraDistance / 2 + 25);
    //camera.position.set(-100,-100,-100);
    //camera.lookAt(b.x, b.y, b.z); 
    //camera.lookAt(0,0,0)
    
    
    //camera.position.set(a.x + cameraDistance, a.y + cameraDistance / 2, a.z + cameraDistance / 2 + 25);
    //camera.lookAt(b.x, b.y, b.z); 
    //camera.lookAt(center)
}
setCameraToLookAtPoints()


// Render loop
function animate() {
    //requestAnimationFrame(animate);
    setCameraToLookAtPoints();
    renderer.render(scene, camera);
    testModel.l3dModel.previewCameraAngle+=0.5;
}
animate();
