/**
 * Diabetes Risk Classification System - Frontend JavaScript
 * Handles client-side validation, password match checking, and interactive form helpers.
 */

document.addEventListener("DOMContentLoaded", function () {
    // 1. Password Match Validation (Registration Page)
    const registerForm = document.getElementById("registerForm");
    const passwordInput = document.getElementById("password");
    const confirmPasswordInput = document.getElementById("confirm_password");
    const passwordMismatchMsg = document.getElementById("passwordMismatchMsg");

    if (registerForm && passwordInput && confirmPasswordInput) {
        function checkPasswordMatch() {
            if (confirmPasswordInput.value && passwordInput.value !== confirmPasswordInput.value) {
                if (passwordMismatchMsg) passwordMismatchMsg.classList.remove("d-none");
                confirmPasswordInput.setCustomValidity("Passwords do not match.");
            } else {
                if (passwordMismatchMsg) passwordMismatchMsg.classList.add("d-none");
                confirmPasswordInput.setCustomValidity("");
            }
        }

        passwordInput.addEventListener("input", checkPasswordMatch);
        confirmPasswordInput.addEventListener("input", checkPasswordMatch);

        registerForm.addEventListener("submit", function (e) {
            if (passwordInput.value.length < 8) {
                alert("Password must be at least 8 characters long.");
                e.preventDefault();
                return;
            }
            if (passwordInput.value !== confirmPasswordInput.value) {
                alert("Passwords do not match. Please re-enter.");
                e.preventDefault();
                return;
            }
        });
    }

    // 2. BMI Calculation Helper on Prediction Page
    const heightInput = document.getElementById("calc_height");
    const weightInput = document.getElementById("calc_weight");
    const bmiTargetInput = document.getElementById("bmi");
    const bmiHelperBadge = document.getElementById("calc_bmi_badge");

    function updateCalculatedBMI() {
        if (!heightInput || !weightInput || !bmiTargetInput) return;
        const h = parseFloat(heightInput.value);
        const w = parseFloat(weightInput.value);

        if (h > 50 && w > 20) {
            const heightInMeters = h / 100.0;
            const calculatedBMI = (w / (heightInMeters * heightInMeters)).toFixed(1);
            bmiTargetInput.value = calculatedBMI;

            if (bmiHelperBadge) {
                bmiHelperBadge.textContent = `Calculated BMI: ${calculatedBMI}`;
                bmiHelperBadge.classList.remove("d-none");
            }
        }
    }

    if (heightInput && weightInput) {
        heightInput.addEventListener("input", updateCalculatedBMI);
        weightInput.addEventListener("input", updateCalculatedBMI);
    }

    // 3. Auto-Dismiss Alerts After 5 Seconds
    const flashAlerts = document.querySelectorAll(".alert.alert-dismissible");
    flashAlerts.forEach(function (alertEl) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alertEl);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });
});

/**
 * Loads predefined example scenarios for demonstration purposes.
 */
function fillPresetSample(type) {
    const fields = {
        pregnancies: document.getElementById("pregnancies"),
        glucose: document.getElementById("glucose"),
        blood_pressure: document.getElementById("blood_pressure"),
        skin_thickness: document.getElementById("skin_thickness"),
        insulin: document.getElementById("insulin"),
        bmi: document.getElementById("bmi"),
        diabetes_pedigree_function: document.getElementById("diabetes_pedigree_function"),
        age: document.getElementById("age")
    };

    if (!fields.glucose) return;

    if (type === "healthy") {
        fields.pregnancies.value = 1;
        fields.glucose.value = 85.0;
        fields.blood_pressure.value = 66.0;
        fields.skin_thickness.value = 29.0;
        fields.insulin.value = 0.0;
        fields.bmi.value = 26.6;
        fields.diabetes_pedigree_function.value = 0.351;
        fields.age.value = 31;
    } else if (type === "high_risk") {
        fields.pregnancies.value = 6;
        fields.glucose.value = 148.0;
        fields.blood_pressure.value = 72.0;
        fields.skin_thickness.value = 35.0;
        fields.insulin.value = 0.0;
        fields.bmi.value = 33.6;
        fields.diabetes_pedigree_function.value = 0.627;
        fields.age.value = 50;
    }
}

/**
 * Resets the prediction form fields to empty state.
 */
function resetPredictionForm() {
    const form = document.getElementById("predictionForm");
    if (form) {
        form.reset();
        const badge = document.getElementById("calc_bmi_badge");
        if (badge) badge.classList.add("d-none");
    }
}
