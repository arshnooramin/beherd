// Progressive enhancements. Every page still works without JavaScript.

// SOS: require a press-and-hold so a stray tap can't alert anyone.
function initSos(form) {
    const button = form.querySelector(".sos");
    const hint = form.querySelector(".sos-hint");
    const idleHint = hint.textContent;
    const holdMs = Number(form.dataset.holdMs);
    let timer = null;
    let confirmed = false;

    form.style.setProperty("--hold-ms", `${holdMs}ms`);

    const start = (event) => {
        if (button.disabled || timer) return;
        event.preventDefault();
        button.classList.add("is-holding");
        hint.textContent = "Keep holding…";
        timer = setTimeout(() => {
            confirmed = true;
            button.classList.replace("is-holding", "is-sending");
            button.disabled = true;
            hint.textContent = "Sending alert…";
            form.submit();
        }, holdMs);
    };

    const cancel = () => {
        if (!timer || confirmed) return;
        clearTimeout(timer);
        timer = null;
        button.classList.remove("is-holding");
        hint.textContent = idleHint;
    };

    form.addEventListener("submit", (event) => {
        if (!confirmed) event.preventDefault();
    });
    button.addEventListener("pointerdown", start);
    button.addEventListener("keydown", (event) => {
        if ((event.key === " " || event.key === "Enter") && !event.repeat) start(event);
    });
    for (const type of ["pointerup", "pointerleave", "pointercancel", "keyup", "blur"]) {
        button.addEventListener(type, cancel);
    }
    button.addEventListener("contextmenu", (event) => event.preventDefault());
}

// Preset form: show contact rows on demand, between the minimum and maximum.
function initContacts(fieldset) {
    const rows = [...fieldset.querySelectorAll("[data-contact-row]")];
    const min = Number(fieldset.dataset.min);
    const addButton = fieldset.querySelector("[data-add-contact]");
    const count = fieldset.querySelector("[data-contact-count]");
    const inputs = (row) => [...row.querySelectorAll("input")];
    const visible = () => rows.filter((row) => !row.hidden);

    const update = () => {
        const shown = visible().length;
        addButton.hidden = shown >= rows.length;
        count.textContent = `${shown} of ${rows.length}`;
        for (const row of rows) {
            row.querySelector("[data-remove-contact]").hidden = shown <= min;
        }
    };

    addButton.addEventListener("click", () => {
        const next = rows.find((row) => row.hidden);
        next.hidden = false;
        inputs(next)[0].focus();
        update();
    });

    fieldset.addEventListener("click", (event) => {
        const button = event.target.closest("[data-remove-contact]");
        if (!button) return;
        const shown = visible();
        const index = shown.indexOf(button.closest("[data-contact-row]"));
        // Shift later rows up so the order on screen is the order saved.
        for (let i = index; i < shown.length - 1; i++) {
            const below = inputs(shown[i + 1]);
            inputs(shown[i]).forEach((input, k) => (input.value = below[k].value));
        }
        const last = shown.at(-1);
        for (const input of inputs(last)) input.value = "";
        last.hidden = true;
        for (const error of fieldset.querySelectorAll("[data-contact-row] .field-error")) error.remove();
        for (const field of fieldset.querySelectorAll("[data-contact-row] .has-error")) {
            field.classList.remove("has-error");
        }
        update();
    });

    update();
}

// Preset page: reveal the codeword on request.
function initReveal(button) {
    const secret = button.parentElement.querySelector("[data-secret]");
    const masked = secret.textContent;
    button.hidden = false;
    button.addEventListener("click", () => {
        const showing = secret.textContent !== masked;
        secret.textContent = showing ? masked : secret.dataset.secret;
        button.textContent = showing ? "Show" : "Hide";
    });
}

document.querySelectorAll(".sos-form").forEach(initSos);
document.querySelectorAll("[data-contacts]").forEach(initContacts);
document.querySelectorAll("[data-reveal]").forEach(initReveal);
