/**
 * Client-Side Validation and Interactivity Engine
 * Enforces data integrity before submitting the form to Python CGI (/cgi-bin/submit.py).
 */

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("registration-form");
    if (!form) return;

    // Field references
    const fullNameInput = document.getElementById("full_name");
    const emailInput = document.getElementById("email");
    const phoneInput = document.getElementById("phone");
    const ageInput = document.getElementById("age");
    const deptSelect = document.getElementById("department");
    const messageInput = document.getElementById("message");
    const charCounter = document.getElementById("char-counter");
    const submitBtn = document.getElementById("submit-btn");
    const resetBtn = document.getElementById("reset-btn");
    const formAlert = document.getElementById("form-alert");

    // Validation Regex Patterns
    const EMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    const PHONE_REGEX = /^[+]?[(]?[0-9]{1,4}[)]?[-\s./0-9]{9,15}$/;
    const NAME_REGEX = /^[A-Za-z\s.'-]+$/;

    /**
     * Updates UI state for a field
     */
    function setFieldState(inputElem, isValid, errorMessage = "") {
        const group = inputElem.closest(".form-group");
        if (!group) return;

        const errorSpan = group.querySelector(".field-error-msg");

        if (isValid) {
            group.classList.remove("has-error");
            group.classList.add("is-valid");
            if (errorSpan) errorSpan.textContent = "";
        } else {
            group.classList.remove("is-valid");
            group.classList.add("has-error");
            if (errorSpan) errorSpan.textContent = errorMessage;
        }
    }

    /**
     * Validates Full Name
     */
    function validateFullName() {
        const val = fullNameInput.value.trim();
        if (!val) {
            setFieldState(fullNameInput, false, "Full name is required.");
            return false;
        }
        if (val.length < 2) {
            setFieldState(fullNameInput, false, "Full name must be at least 2 characters.");
            return false;
        }
        if (val.length > 80) {
            setFieldState(fullNameInput, false, "Full name cannot exceed 80 characters.");
            return false;
        }
        if (!NAME_REGEX.test(val)) {
            setFieldState(fullNameInput, false, "Letters, spaces, hyphens, and apostrophes only.");
            return false;
        }
        setFieldState(fullNameInput, true);
        return true;
    }

    /**
     * Validates Email Address
     */
    function validateEmail() {
        const val = emailInput.value.trim();
        if (!val) {
            setFieldState(emailInput, false, "Email address is required.");
            return false;
        }
        if (!EMAIL_REGEX.test(val)) {
            setFieldState(emailInput, false, "Enter a valid email address (e.g. name@university.edu).");
            return false;
        }
        setFieldState(emailInput, true);
        return true;
    }

    /**
     * Validates Phone Number
     */
    function validatePhone() {
        const val = phoneInput.value.trim();
        const digitsOnly = val.replace(/\D/g, "");
        if (!val) {
            setFieldState(phoneInput, false, "Phone number is required.");
            return false;
        }
        if (digitsOnly.length < 10 || digitsOnly.length > 15) {
            setFieldState(phoneInput, false, "Phone number must have between 10 and 15 digits.");
            return false;
        }
        if (!PHONE_REGEX.test(val)) {
            setFieldState(phoneInput, false, "Please enter a valid phone format (e.g., +1 234-567-8901).");
            return false;
        }
        setFieldState(phoneInput, true);
        return true;
    }

    /**
     * Validates Age
     */
    function validateAge() {
        const val = ageInput.value.trim();
        if (!val) {
            setFieldState(ageInput, false, "Age is required.");
            return false;
        }
        const num = parseInt(val, 10);
        if (isNaN(num) || num < 16 || num > 99) {
            setFieldState(ageInput, false, "Age must be between 16 and 99.");
            return false;
        }
        setFieldState(ageInput, true);
        return true;
    }

    /**
     * Validates Department Selection
     */
    function validateDepartment() {
        const val = deptSelect.value.trim();
        if (!val) {
            setFieldState(deptSelect, false, "Please choose a course or department.");
            return false;
        }
        setFieldState(deptSelect, true);
        return true;
    }

    /**
     * Validates Message Length
     */
    function validateMessage() {
        const val = messageInput.value;
        if (val.length > 1000) {
            setFieldState(messageInput, false, "Message cannot exceed 1000 characters.");
            return false;
        }
        setFieldState(messageInput, true);
        return true;
    }

    // Attach real-time input listeners
    fullNameInput.addEventListener("blur", validateFullName);
    fullNameInput.addEventListener("input", () => {
        if (fullNameInput.closest(".form-group").classList.contains("has-error")) {
            validateFullName();
        }
    });

    emailInput.addEventListener("blur", validateEmail);
    emailInput.addEventListener("input", () => {
        if (emailInput.closest(".form-group").classList.contains("has-error")) {
            validateEmail();
        }
    });

    phoneInput.addEventListener("blur", validatePhone);
    phoneInput.addEventListener("input", () => {
        if (phoneInput.closest(".form-group").classList.contains("has-error")) {
            validatePhone();
        }
    });

    ageInput.addEventListener("blur", validateAge);
    ageInput.addEventListener("input", () => {
        if (ageInput.closest(".form-group").classList.contains("has-error")) {
            validateAge();
        }
    });

    deptSelect.addEventListener("change", validateDepartment);

    messageInput.addEventListener("input", () => {
        const currentLength = messageInput.value.length;
        if (charCounter) {
            charCounter.textContent = `${currentLength} / 1000`;
            if (currentLength > 1000) {
                charCounter.style.color = "var(--danger)";
            } else {
                charCounter.style.color = "var(--text-muted)";
            }
        }
        validateMessage();
    });

    // Form Submission Interception
    form.addEventListener("submit", (event) => {
        // Run all client validations
        const isNameValid = validateFullName();
        const isEmailValid = validateEmail();
        const isPhoneValid = validatePhone();
        const isAgeValid = validateAge();
        const isDeptValid = validateDepartment();
        const isMsgValid = validateMessage();

        const isFormValid = isNameValid && isEmailValid && isPhoneValid && isAgeValid && isDeptValid && isMsgValid;

        if (!isFormValid) {
            // Halt browser POST request to CGI
            event.preventDefault();

            // Display error alert banner
            if (formAlert) {
                formAlert.style.display = "flex";
                formAlert.className = "alert alert-danger animate-fade-in";
                formAlert.innerHTML = `
                    <span>⚠️ <strong>Form Validation Error:</strong> Please correct the highlighted errors before submitting to the CGI server.</span>
                    <span class="alert-close" onclick="this.parentElement.style.display='none'">✕</span>
                `;
            }

            // Scroll to the first erroneous input
            const firstErrorField = form.querySelector(".form-group.has-error input, .form-group.has-error select, .form-group.has-error textarea");
            if (firstErrorField) {
                firstErrorField.focus();
            }
            return false;
        }

        // Hide alert if previously shown
        if (formAlert) {
            formAlert.style.display = "none";
        }

        // Show loading state on submit button while the HTTP POST request is sent to Python CGI
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<span class="btn-spinner"></span> Submitting via HTTP POST to Python CGI...`;

        // Standard HTML form submission continues to /cgi-bin/submit.py
        return true;
    });

    // Reset Form Handler
    if (resetBtn) {
        resetBtn.addEventListener("click", () => {
            const groups = form.querySelectorAll(".form-group");
            groups.forEach(g => {
                g.classList.remove("has-error", "is-valid");
                const errSpan = g.querySelector(".field-error-msg");
                if (errSpan) errSpan.textContent = "";
            });
            if (charCounter) charCounter.textContent = "0 / 1000";
            if (formAlert) formAlert.style.display = "none";
        });
    }
});
