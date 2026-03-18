
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


function safeguard(case_id, criterion_id, value) {
    url = '/safeguard_diagnosis?case_id=' + case_id + '&criterion_id=' + criterion_id + '&value=' + value
    $.getJSON(url,
        function(data) {
      //do nothing
    });
    return false;
};

function tutorial(idCriterion) {
    var modal = document.getElementById("tutorialModal");
    var frame = document.getElementById("tutorialFrame");
    var span = document.getElementsByClassName("close")[0];

    frame.src = '/tutorial/' + idCriterion;
    modal.style.display = "block";

    span.onclick = function() {
        modal.style.display = "none";
        frame.src = "";
    };

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
            frame.src = "";
        }
    };
}

// Function to update unanswered red borders
function updateUnansweredBorders() {
    const diagnosisGroup = document.querySelector('.diagnosis-options');
    const radios = diagnosisGroup.querySelectorAll('input[type="radio"]:not(:disabled)');
    const unansweredLabel = diagnosisGroup.querySelector('input[type="radio"]:disabled + label');

    let isAnswered = Array.from(radios).some(r => r.checked);

    if (unansweredLabel) {
        unansweredLabel.style.border = isAnswered ? '1px solid #bbb' : '1px solid #ff9999';
    }
}

// Run on page load
window.addEventListener('load', updateUnansweredBorders);

// Update whenever any radio is clicked
document.addEventListener('change', function(e) {
    if (e.target.matches('.diagnosis-options input[type="radio"]')) {
        updateUnansweredBorders();
    }
});

window.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.case_img').forEach(img => {
        let scale = 1;
        let translateX = 0;
        let translateY = 0;
        let isDragging = false;
        let hasMoved = false;
        let dragStartX = 0;
        let dragStartY = 0;
        
        img.style.transition = 'transform 0.1s ease';
        img.style.cursor = 'default';

        // Zoom with Ctrl + Mouse Wheel
        img.addEventListener('wheel', function(e) {
            if (e.ctrlKey) {
                e.preventDefault();
                
                const rect = img.getBoundingClientRect();
                const mouseX = e.clientX - rect.left;
                const mouseY = e.clientY - rect.top;
                
                const imgCenterX = rect.width / 2;
                const imgCenterY = rect.height / 2;
                
                const mouseFromCenterX = mouseX - imgCenterX;
                const mouseFromCenterY = mouseY - imgCenterY;
                
                const oldScale = scale;
                
                if (e.deltaY < 0) {
                    scale = Math.min(scale + 0.1, 3);
                } else {
                    scale = Math.max(scale - 0.1, 1);
                    
                    if (scale === 1) {
                        translateX = 0;
                        translateY = 0;
                    }
                }
                
                if (scale > 1) {
                    const scaleDiff = scale - oldScale;
                    translateX -= mouseFromCenterX * scaleDiff;
                    translateY -= mouseFromCenterY * scaleDiff;
                }
                
                updateTransform(img);
                img.style.cursor = scale > 1 ? 'grab' : 'default';
            }
        });

        img.addEventListener('mousedown', function(e) {
            if (scale > 1) {
                isDragging = true;
                hasMoved = false;
                dragStartX = e.clientX - translateX;
                dragStartY = e.clientY - translateY;
                img.style.cursor = 'grabbing';
                img.style.transition = 'none';
                e.preventDefault();
                e.stopPropagation();
            }
        });

        img.addEventListener('mousemove', function(e) {
            if (isDragging && scale > 1) {
                const newTranslateX = e.clientX - dragStartX;
                const newTranslateY = e.clientY - dragStartY;
                
                if (Math.abs(newTranslateX - translateX) > 3 || Math.abs(newTranslateY - translateY) > 3) {
                    hasMoved = true;
                }
                
                translateX = newTranslateX;
                translateY = newTranslateY;
                updateTransform(img);
            }
        });

        img.addEventListener('mouseup', function(e) {
            if (isDragging) {
                isDragging = false;
                img.style.cursor = 'grab';
                img.style.transition = 'transform 0.1s ease';
                
                if (hasMoved) {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                }
            }
        });

        img.addEventListener('click', function(e) {
            if (scale > 1 && hasMoved) {
                e.preventDefault();
                e.stopPropagation();
                e.stopImmediatePropagation();
            }
        }, true);

        img.addEventListener('mouseleave', function(e) {
            if (isDragging) {
                isDragging = false;
                img.style.cursor = 'grab';
                img.style.transition = 'transform 0.1s ease';
            }
        });

        img.addEventListener('dblclick', function(e) {
            e.preventDefault();
            e.stopPropagation();
            scale = 1;
            translateX = 0;
            translateY = 0;
            img.style.transition = 'transform 0.3s ease';
            updateTransform(img);
            img.style.cursor = 'default';
            setTimeout(() => {
                img.style.transition = 'transform 0.1s ease';
            }, 300);
        });

        function updateTransform(element) {
            element.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
            element.style.transformOrigin = 'center center';
        }
    });
});

