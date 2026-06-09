
const gallery = document.getElementById('gallery');
const viewer = new Viewer(gallery, {
    title: 0,
    toolbar: {
        zoomIn: 1,
        zoomOut: 1,
        oneToOne: 1,
        reset: 1,
        prev: 1,
        play: 0,
        next: 1,
        rotateLeft: 0,
        rotateRight: 0,
        flipHorizontal: 0,
        flipVertical: 0,
    },
    movable: 1,
    tooltip: 1, //gives zoom ratio after a change
});