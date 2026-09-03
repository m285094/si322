//script.js

let counter = 0;

function increaseCounter() {
    counter++;
    document.getElementById('counterDisplay').textContent = counter;
}

function decreaseCounter() {
    counter--;
    document.getElementById('counterDisplay').textContent = counter;
}

function resetCounter() {
    counter = 0;
    document.getElementById('counterDisplay').textContent = counter;
}