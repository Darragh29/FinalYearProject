document.addEventListener('DOMContentLoaded', function () {
    const video = document.getElementById('video');
    const captureBtn = document.getElementById('captureBtn');
    const canvas = document.getElementById('canvas');
    const capturedImageInput = document.getElementById('capturedImageInput');
    const uploadedInput = document.getElementById('image');
    const previewImage = document.getElementById('uploadedPreview')
    const orText = document.getElementById('orText');

    //Start the camera and show live feed
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function (stream) {
            console.log("Camera accessed");
            video.srcObject = stream;
            video.play();
        })
        .catch(function (err) {
            console.error("Camera access failed: ", err);
        });

    //Handle image file upload
    uploadedInput.addEventListener('change', function () {
        if (this.files && this.files[0]) {
            const reader = new FileReader();
            reader.onload = function (e) {
                previewImage.src = e.target.result;
                previewImage.style.display = 'block'; //Preview is shown

                //Hide camera elements
                video.style.display = 'none';
                captureBtn.style.display = 'none';
                canvas.style.display = 'none';
                orText.style.display = 'none';
            };
            reader.readAsDataURL(this.files[0]);
        }
    });

    //Handle capture button click
    captureBtn.addEventListener('click', function () {
        console.log("Capture button clicked!");

        let countdown = 3;
        captureBtn.disabled = true;

        const countdownInterval = setInterval(function () {
            captureBtn.textContent = `Capture in ${countdown}`;
            countdown--;
            if (countdown < 0) {
                clearInterval(countdownInterval);
                captureBtn.textContent = 'Capture';
                captureImage();
            }
        }, 1000);
    });

    //Function to capture an image from the video stream
    function captureImage() {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        const imageDataUrl = canvas.toDataURL('image/jpeg');
        capturedImageInput.value = imageDataUrl;

        //Show captured image in canvas
        canvas.style.display = 'block';  //Make the canvas visible
        video.style.display = 'none';
        captureBtn.style.display = 'none';
        orText.style.display = 'none';

        //Show preview image as <img> tag
        previewImage.src = imageDataUrl;
        previewImage.style.display = 'block';  //Ensure preview is shown

        //Stop the camera after capturing
        let stream = video.srcObject;
        let tracks = stream.getTracks();
        tracks.forEach(track => track.stop());
    }
});
