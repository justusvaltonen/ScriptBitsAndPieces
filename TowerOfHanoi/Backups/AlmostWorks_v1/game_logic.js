
// Initialize the game with 3 disks
let disks = 3;
let rods = {
    rod1: [],
    rod2: [],
    rod3: []
};

// ADDED FEATURE: Move counter, Drag n' drop
let moveCount = 0;
let draggedDisk = null;
let draggedFromRod = null;

// ADDED FEATURE: Calculate minimum moves
const minMoves = Math.pow(2, disks) - 1;

// Start the game
function initGame() {
    rods.rod1 = Array.from({ length: disks }, (_, i) => disks - i);
    rods.rod2 = [];
    rods.rod3 = [];

    // ADDED FEATURE: Move counter, 2 lines
    moveCount = 0;
    document.getElementById('move-count').textContent = moveCount;

    // BUG FIX: Added line
    minMoves = Math.pow(2, disks) - 1;

    // ADDED FEATURE: Calculate minimum moves
    document.getElementById('min-moves').textContent = minMoves;

    renderRods();
    document.getElementById('message').textContent = '';

    // ADDED FEATURE: Animations
    document.getElementById('message').classList.remove('win-animation');

    // ADDED FEATURE: Drag n' drop, 2 lines
    renderRods();
    addDragAndDropListeners();
}

// ADDED FEATURE: Change the number of disks
function changeDiskCount() {
    disks = parseInt(document.getElementById('disk-count').value);
    initGame();
}

// Render the rods and disks
function renderRods() {

    // ADDED 2 LINES: Bugfix
    const maxDiskWidth = 180; // Maximum width for the largest disk
    const widthStep = maxDiskWidth / disks;

    for (let rod in rods) {
        const rodElement = document.getElementById(rod);
        rodElement.innerHTML = '';

        // ADDED FEATURE: Drag n' drop
        rodElement.className = 'rod';

        rods[rod].forEach(size => {
            const disk = document.createElement('div');
            disk.className = 'disk';
            disk.style.width = `${size * 30}px`;
            disk.style.marginLeft = `${(6 - size) * 15}px`;
            disk.textContent = size;

            // ADDED FEATURE: Drag n' drop 2 lines
            disk.draggable = true;
            disk.dataset.size = size;

            rodElement.appendChild(disk);
        });
    }
}

// ADDED FEATURE: Drag n' drop, 5 functions
// Add drag and drop event listeners
function addDragAndDropListeners() {
    document.querySelectorAll('.disk').forEach(disk => {
        disk.addEventListener('dragstart', handleDragStart);
    });

    document.querySelectorAll('.rod').forEach(rod => {
        rod.addEventListener('dragover', handleDragOver);
        rod.addEventListener('dragleave', handleDragLeave);
        rod.addEventListener('drop', handleDrop);
    });
}

// Handle drag start
function handleDragStart(e) {
    draggedDisk = this;
    draggedFromRod = this.parentNode.id;
    e.dataTransfer.setData('text/plain', this.dataset.size);
    setTimeout(() => this.classList.add('dragging'), 0);
}

// Handle drag over
function handleDragOver(e) {
    e.preventDefault();
    this.classList.add('highlight');
}

// Handle drag leave
function handleDragLeave() {
    this.classList.remove('highlight');
}

// Handle drop
function handleDrop(e) {
    e.preventDefault();
    this.classList.remove('highlight');

    const targetRodId = this.id;
    const diskSize = parseInt(e.dataTransfer.getData('text/plain'));

    // Check if the move is valid
    const targetRod = rods[targetRodId];
    if (targetRod.length > 0 && targetRod[targetRod.length - 1] < diskSize) {
        document.getElementById('message').textContent = 'Invalid move!';
        return;
    }

    // Move the disk
    const sourceRod = rods[draggedFromRod];
    if (sourceRod.length === 0 || sourceRod[sourceRod.length - 1] !== diskSize) {
        return;
    }

    sourceRod.pop();
    targetRod.push(diskSize);
    moveCount++;
    document.getElementById('move-count').textContent = moveCount;

    renderRods();
    addDragAndDropListeners();

    // Check for win

<!--    if (rods.rod3.length === disks) {							-->
<!--        document.getElementById('message').textContent =					-->
<!--            `You win in ${moveCount} moves! ${moveCount === minMoves ? 'Perfect!' : ''}`;	-->
    if (rods.rod3.length === disks) {
        const messageElement = document.getElementById('message');
        messageElement.textContent = `You win in ${moveCount} moves! ${moveCount === minMoves ? 'Perfect!' : ''}`;
        messageElement.classList.add('win-animation');
    } else {
        document.getElementById('message').textContent = '';
    }
}



/*
// REMOVED FUNCTION: Relplaced with Drag n' drop
// Move disk from source rod to target rod
function moveDisk(source, target) {
    const sourceRod = rods[source];
    const targetRod = rods[target];

    if (sourceRod.length === 0) {
        document.getElementById('message').textContent = `No disk on ${source}!`;
        return;
    }

    const diskSize = sourceRod[sourceRod.length - 1];

    if (targetRod.length > 0 && targetRod[targetRod.length - 1] < diskSize) {
        document.getElementById('message').textContent = 'Invalid move!';
        return;
    }

    sourceRod.pop();
    targetRod.push(diskSize);

    // ADDED FEATURE: Move counter, 2 lines
    moveCount++;
    document.getElementById('move-count').textContent = moveCount;

    renderRods();

    // Check for win
    if (rods.rod3.length === disks) {
        document.getElementById('message').textContent =
            `You win in ${moveCount} moves! ${moveCount === minMoves ? 'Perfect!' : ''}`;

        // document.getElementById('message').textContent = 'You win!';

    } else {
        document.getElementById('message').textContent = '';
    }
}
*/

function resetGame() {
    initGame();
}

window.onload = initGame;

// Start the game
// REMOVED LINE: from first draft
// initGame();

