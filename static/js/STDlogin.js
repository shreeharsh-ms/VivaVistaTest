document.addEventListener("DOMContentLoaded", function () {
    var canvas = document.createElement("canvas");
    var width = canvas.width = window.innerWidth * 0.75;
    var height = canvas.height = window.innerHeight * 0.75;
    document.body.appendChild(canvas);

    var gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    if (!gl) {
        alert('WebGL not supported in your browser');
        return;
    }

    var mouse = { x: 0, y: 0 };

    var numMetaballs = 30;
    var metaballs = [];

    for (var i = 0; i < numMetaballs; i++) {
        var radius = Math.random() * 60 + 10;
        metaballs.push({
            x: Math.random() * (width - 2 * radius) + radius,
            y: Math.random() * (height - 2 * radius) + radius,
            vx: (Math.random() - 0.5) * 3,
            vy: (Math.random() - 0.5) * 3,
            r: radius * 0.75
        });
    }

    var vertexShaderSrc = `
        attribute vec2 position;

        void main() {
            gl_Position = vec4(position, 0.0, 1.0);
        }
    `;

    var fragmentShaderSrc = `
        precision highp float;

        const float WIDTH = ` + (width >> 0) + `.0;
        const float HEIGHT = ` + (height >> 0) + `.0;

        uniform vec3 metaballs[` + numMetaballs + `];

        void main(){
            float x = gl_FragCoord.x;
            float y = gl_FragCoord.y;

            float sum = 0.0;
            for (int i = 0; i < ` + numMetaballs + `; i++) {
                vec3 metaball = metaballs[i];
                float dx = metaball.x - x;
                float dy = metaball.y - y;
                float radius = metaball.z;

                sum += (radius * radius) / (dx * dx + dy * dy);
            }

            if (sum >= 0.99) {
                gl_FragColor = vec4(mix(vec3(x / WIDTH, y / HEIGHT, 1.0), vec3(0, 0, 0), max(0.0, 1.0 - (sum - 0.99) * 100.0)), 1.0);
                return;
            }

            gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
        }
    `;

    var vertexShader = compileShader(vertexShaderSrc, gl.VERTEX_SHADER);
    var fragmentShader = compileShader(fragmentShaderSrc, gl.FRAGMENT_SHADER);

    var program = gl.createProgram();
    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);
    gl.useProgram(program);

    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
        console.error("Could not initialize shaders");
        return;
    }

    var vertexData = new Float32Array([
        -1.0, 1.0,   // top left
        -1.0, -1.0,  // bottom left
        1.0, 1.0,    // top right
        1.0, -1.0    // bottom right
    ]);

    var vertexDataBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, vertexDataBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, vertexData, gl.STATIC_DRAW);

    var positionHandle = gl.getAttribLocation(program, 'position');
    gl.enableVertexAttribArray(positionHandle);
    gl.vertexAttribPointer(positionHandle, 2, gl.FLOAT, false, 2 * 4, 0);

    var metaballsHandle = gl.getUniformLocation(program, 'metaballs');
    if (metaballsHandle === -1) {
        console.error("Uniform 'metaballs' not found.");
        return;
    }

    function loop() {
        for (var i = 0; i < numMetaballs; i++) {
            var metaball = metaballs[i];
            metaball.x += metaball.vx;
            metaball.y += metaball.vy;

            if (metaball.x < metaball.r || metaball.x > width - metaball.r) metaball.vx *= -1;
            if (metaball.y < metaball.r || metaball.y > height - metaball.r) metaball.vy *= -1;
        }

        var dataToSendToGPU = new Float32Array(3 * numMetaballs);
        for (var i = 0; i < numMetaballs; i++) {
            var baseIndex = 3 * i;
            var mb = metaballs[i];
            dataToSendToGPU[baseIndex + 0] = mb.x;
            dataToSendToGPU[baseIndex + 1] = mb.y;
            dataToSendToGPU[baseIndex + 2] = mb.r;
        }

        gl.uniform3fv(metaballsHandle, dataToSendToGPU);

        // Clear the canvas before drawing
        gl.clear(gl.COLOR_BUFFER_BIT);

        // Draw
        gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);

        requestAnimationFrame(loop);
    }

    loop();

    function compileShader(shaderSource, shaderType) {
        var shader = gl.createShader(shaderType);
        gl.shaderSource(shader, shaderSource);
        gl.compileShader(shader);

        if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
            console.error("Shader compile failed with: " + gl.getShaderInfoLog(shader));
            return null;
        }

        return shader;
    }
    currentSlide(1)
});

let slideIndex = 1;
showSlides(slideIndex);

// Function to display the current slide
function currentSlide(n) {
    showSlides(slideIndex = n);
}

// Function to show the slides and manage the dots
function showSlides(n) {
    let slides = document.getElementsByClassName("slide");
    let dots = document.getElementsByClassName("dot");

    if (n > slides.length) {
        slideIndex = 1;
    }

    if (n < 1) {
        slideIndex = slides.length;
    }

    // Hide all slides initially
    for (let i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }

    // Remove "active" class from all dots
    for (let i = 0; i < dots.length; i++) {
        dots[i].classList.remove("active");
    }

    // Display the current slide and activate the corresponding dot
    slides[slideIndex - 1].style.display = "block";
    dots[slideIndex - 1].classList.add("active");
}
