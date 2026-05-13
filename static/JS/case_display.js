
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

function safeguard(case_id, criterion_id, value, category) {
    url = '/safeguard_diagnosis?case_id=' + case_id + '&criterion_id=' + criterion_id + '&value=' + value + '&category=' + category;
    
    $.getJSON(url, function(data){});
    return false;
}

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

function case_diagnose(userId){
    open ('/case_diagnose/' + userId, '_self')
}

function user_home(){
    open ('/user_home/', '_self')
}

function updateValue(cat_name, case_id, criterion_id, category){
    slider_name = cat_name + 'TrustScale';
    output_name = cat_name + 'TrustValue';
    var slider = document.getElementById(slider_name);
    var output = document.getElementById(output_name);
    var value = slider.value;
    output.innerHTML = value;
    safeguard(case_id, criterion_id, slider.value, category)
    return false;
}

function save_number(case_id, criterion_id, category){
    var input = document.getElementById(criterion_id);
    var value = input.value;
    var max = input.max;
    var min = input.min;
    
    if (parseInt(value) > parseInt(max)){
        value = max;
        input.value = value;
    }
    
    if (parseInt(value) < parseInt(min)){
        value = min;
        input.value = value;
    }
    
    safeguard(case_id, criterion_id, value, category);
}

function updateVisibility(){
    var prerequisites = document.getElementsByClassName( 'category_prerequisite' );
    for (let i = 0; i < prerequisites.length; i++){
        var prerequisite = prerequisites[i];
        var conditions = JSON.parse(prerequisite.dataset.conditions);
        var display = false;
        for (let j = 0; j < conditions.length; j++){
            var requirement_id = conditions[j];
            var requirement = document.getElementById(requirement_id);
            if (requirement == null){
                var requirement = document.getElementById(requirement_id + 'Yes');
            }
            var checked = requirement.checked;
            if (checked == undefined){
                if (requirement.value != undefined){
                    var checked = true;
                }
            }
            if (checked){
                display = true;
            }
        }
        var category_name = prerequisite.id.split( '_prerequisites' )[0];
        var category = document.getElementById(category_name);
        if (display){
            category.style.display = 'block';
        }
        else{
            category.style.display = 'none';
        }
    }
}

// Function to update unanswered red borders
function updateUnansweredBorders() {
    document.querySelectorAll('.options').forEach(function(optionGroup) {
        const radios = optionGroup.querySelectorAll('input[type="radio"]:not(:disabled)');
        const unansweredLabel = optionGroup.querySelector('input[type="radio"]:disabled + label');

        let isAnswered = Array.from(radios).some(r => r.checked);

        if (unansweredLabel) {
            unansweredLabel.style.border = isAnswered ? '1px solid #bbb' : '1px solid #ff9999';
        }
    });
}

// Run on page load
window.addEventListener('load', updateUnansweredBorders);
window.addEventListener('load', updateVisibility);


// Update whenever any radio is clicked
document.addEventListener('change', function(e) {
    if (e.target.matches('.options input[type="radio"]')) {
        updateUnansweredBorders();
    }
});

window.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.case_img').forEach(img => {
        let scale = 1;
        let translateX = 0;
        let translateY = 0;
        let isDragging = false;
        let hasMoved = false; // Track if mouse has moved during drag
        let dragStartX = 0;
        let dragStartY = 0;
        
        img.style.transition = 'transform 0.1s ease';
        img.style.cursor = 'default';

        // Zoom with Ctrl + Mouse Wheel
        img.addEventListener('wheel', function(e) {
            if (e.ctrlKey) {
                e.preventDefault();
                
                // Get mouse position relative to the image
                const rect = img.getBoundingClientRect();
                const mouseX = e.clientX - rect.left;
                const mouseY = e.clientY - rect.top;
                
                // Calculate mouse position in the transformed coordinate space
                const imgCenterX = rect.width / 2;
                const imgCenterY = rect.height / 2;
                
                const mouseFromCenterX = mouseX - imgCenterX;
                const mouseFromCenterY = mouseY - imgCenterY;
                
                const oldScale = scale;
                
                // Slower, smoother zoom increments
                if (e.deltaY < 0) {
                    scale = Math.min(scale + 0.1, 3); // Zoom in slower (max 5x)
                } else {
                    scale = Math.max(scale - 0.1, 1); // Zoom out slower (min 1x)
                    
                    if (scale === 1) {
                        translateX = 0;
                        translateY = 0;
                    }
                }
                
                // Adjust translation to zoom toward mouse cursor
                if (scale > 1) {
                    const scaleDiff = scale - oldScale;
                    translateX -= mouseFromCenterX * scaleDiff;
                    translateY -= mouseFromCenterY * scaleDiff;
                }
                
                updateTransform(img);
                img.style.cursor = scale > 1 ? 'grab' : 'default';
            }
        });

        // Mouse down - start dragging
        img.addEventListener('mousedown', function(e) {
            if (scale > 1) {
                isDragging = true;
                hasMoved = false; // Reset movement flag
                dragStartX = e.clientX - translateX;
                dragStartY = e.clientY - translateY;
                img.style.cursor = 'grabbing';
                img.style.transition = 'none';
                e.preventDefault();
                e.stopPropagation(); // Stop event from bubbling
            }
        });

        // Mouse move - drag the image
        img.addEventListener('mousemove', function(e) {
            if (isDragging && scale > 1) {
                const newTranslateX = e.clientX - dragStartX;
                const newTranslateY = e.clientY - dragStartY;
                
                // If mouse has moved more than a few pixels, mark as moved
                if (Math.abs(newTranslateX - translateX) > 3 || Math.abs(newTranslateY - translateY) > 3) {
                    hasMoved = true;
                }
                
                translateX = newTranslateX;
                translateY = newTranslateY;
                updateTransform(img);
            }
        });

        // Mouse up - stop dragging
        img.addEventListener('mouseup', function(e) {
            if (isDragging) {
                isDragging = false;
                img.style.cursor = 'grab';
                img.style.transition = 'transform 0.1s ease';
                
                // Prevent click event if we moved the image
                if (hasMoved) {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                }
            }
        });

        // Click event - prevent gallery opening if we dragged
        img.addEventListener('click', function(e) {
            if (scale > 1 && hasMoved) {
                e.preventDefault();
                e.stopPropagation();
                e.stopImmediatePropagation();
            }
        }, true); // Use capture phase

        // Mouse leave - stop dragging if user leaves the image
        img.addEventListener('mouseleave', function(e) {
            if (isDragging) {
                isDragging = false;
                img.style.cursor = 'grab';
                img.style.transition = 'transform 0.1s ease';
            }
        });

        // Double-click to reset zoom
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

        // Helper function to update transform
        function updateTransform(element) {
            element.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
            element.style.transformOrigin = 'center center';
        }
    });
});

