document.addEventListener("DOMContentLoaded", function () {
    const addEmailBtn = document.getElementById('add-email-btn');
    const emailWindow = document.getElementById('email-window');
    const doneBtn = document.getElementById('done-btn');
    const addEmail = document.getElementById('add-email');
    const otpBoxes = document.querySelectorAll('.otp-box');

    // Toggle the email window slide down
    addEmailBtn.addEventListener('click', function () {
        if (emailWindow.style.display === 'block') {
            emailWindow.style.display = 'none';
        } else {
            emailWindow.style.display = 'block';
        }
    });

    // Done button event listener
    doneBtn.addEventListener('click', function () {
        emailWindow.style.display = 'none';
        addEmailBtn.classList.add('green');
        document.querySelector('.email-label').textContent = document.getElementById('email-input').value;
    });

    // Automatically move focus to the next OTP box
    otpBoxes.forEach((box, index) => {
        box.addEventListener('input', function () {
            if (box.value.length === 1 && index < otpBoxes.length - 1) {
                otpBoxes[index + 1].focus();
            }
        });
    });
});
