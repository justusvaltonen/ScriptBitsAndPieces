// Initialize the game with the selected number of disks
let disks = 3;
let rods = {
    rod1: [],
    rod2: [],
    rod3: []
};
let moveCount = 0;
let draggedDisk = null;
let draggedFromRod = null;
let minMoves = Math.pow(2, disks) - 1;

// Start the game
function initGame() {
    rods.rod1 = Array.from({ length: disks }, (_, i) => disks - i);
    rods.rod2 = [];
    rods.rod3 = [];
    moveCount = 0;
    minMoves = Math.pow(2, disks) - 1;
    document.getElementById('move-count').textContent = moveCount;
    document.getElementById('min-moves').textContent = minMoves;
    document.getElementById('message').textContent = '';
    document.getElementById('message').classList.remove('win-animation');
    renderRods();
    addDragAndDropListeners();
}

// Change the number of disks
function changeDiskCount() {
    disks = parseInt(document.getElementById('disk-count').value);
    initGame();
}

// Render the rods and disks
function renderRods() {
    const rodWidth = 200;
    const maxDiskWidth = 180;
    const diskHeight = 30;
    const widthStep = maxDiskWidth / disks;

    for (let rod in rods) {
        const rodElement = document.getElementById(rod);
        rodElement.innerHTML = '';
        rodElement.className = 'rod';
        rodElement.style.height = `${disks * diskHeight + 20}px`;

        rods[rod].forEach((size) => {
            const disk = document.createElement('div');
            disk.className = 'disk';
            disk.style.width = `${size * widthStep}px`;
            disk.style.marginLeft = `${(maxDiskWidth - size * widthStep) / 2}px`;
            disk.style.background = `linear-gradient(to bottom, hsl(${(size * 30) % 360}, 70%, 50%), hsl(${(size * 30 + 20) % 360}, 70%, 40%))`;
            disk.textContent = size;
            disk.draggable = true;
            disk.dataset.size = size;
            rodElement.appendChild(disk);
        });
    }
}

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
    if (rods.rod3.length === disks) {
        const messageElement = document.getElementById('message');
        messageElement.textContent = `You win in ${moveCount} moves! ${moveCount === minMoves ? 'Perfect!' : ''}`;
        messageElement.classList.add('win-animation');
    } else {
        document.getElementById('message').textContent = '';
    }
}

// Reset the game
function resetGame() {
    initGame();
}

// Start the game when the page loads
window.onload = initGame;
