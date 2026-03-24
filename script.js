// Initialize Lucide Icons
lucide.createIcons();

// Sticky Navbar Effect
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        navbar.style.background = 'var(--bg)';
        navbar.style.padding = '1rem 0';
        navbar.style.boxShadow = 'none';
        navbar.style.borderBottom = '1px solid var(--gray-mid)';
    } else {
        navbar.style.background = 'transparent';
        navbar.style.padding = '1.5rem 0';
        navbar.style.borderBottom = '1px solid transparent';
    }
});

// Hamburger Menu Toggle
const hamburgerBtn = document.getElementById('hamburgerBtn');
const mobileNav = document.getElementById('mobileNav');
const closeMobileNav = document.getElementById('closeMobileNav');
const mobileNavLeadBtn = document.getElementById('mobileNavLeadBtn');
const mobileStickyLeadBtn = document.getElementById('mobileStickyLeadBtn');
const leadModal = document.getElementById('leadModal');
const leadModalContent = leadModal ? leadModal.querySelector('.modal-content') : null;
let lastFocusedElement = null;

function openMobileMenu() {
    hamburgerBtn.classList.add('open');
    mobileNav.classList.add('open');
    hamburgerBtn.setAttribute('aria-expanded', 'true');
    mobileNav.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
}

function closeMobileMenu() {
    hamburgerBtn.classList.remove('open');
    mobileNav.classList.remove('open');
    hamburgerBtn.setAttribute('aria-expanded', 'false');
    mobileNav.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
}

if (hamburgerBtn) {
    hamburgerBtn.addEventListener('click', () => {
        if (hamburgerBtn.classList.contains('open')) {
            closeMobileMenu();
        } else {
            openMobileMenu();
        }
    });
}

if (closeMobileNav) {
    closeMobileNav.addEventListener('click', closeMobileMenu);
}

if (mobileNavLeadBtn) {
    mobileNavLeadBtn.addEventListener('click', () => {
        closeMobileMenu();
        openLeadModal();
    });
}

if (mobileStickyLeadBtn) {
    mobileStickyLeadBtn.addEventListener('click', openLeadModal);
}

// Close mobile menu when any nav link is clicked
document.querySelectorAll('.mobile-nav-link').forEach(link => {
    link.addEventListener('click', closeMobileMenu);
});

// Close mobile menu on ESC
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && mobileNav && mobileNav.classList.contains('open')) {
        closeMobileMenu();
    }
});

// Scrollspy Logic
const sections = document.querySelectorAll('section[id]');
const navLinksDesktop = document.querySelectorAll('.nav-links a[href^="#"]');
const navLinksMobile = document.querySelectorAll('.mobile-nav-link[href^="#"]');

const scrollSpyObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const currentId = entry.target.getAttribute('id');
            const activeHref = `#${currentId}`;
            
            navLinksDesktop.forEach(link => {
                link.classList.toggle('active', link.getAttribute('href') === activeHref);
            });
            navLinksMobile.forEach(link => {
                link.classList.toggle('active', link.getAttribute('href') === activeHref);
            });
        }
    });
}, { rootMargin: '-20% 0px -70% 0px' });

sections.forEach(section => {
    scrollSpyObserver.observe(section);
});

// Scroll Animations (Intersection Observer)
const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1
};

const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

document.querySelectorAll('.fade-in-up').forEach(element => {
    observer.observe(element);
});

// FAQ Accordion — global function for onclick + delegated listener
function toggleFaq(btn) {
    const item = btn.closest('.faq-item');
    if (!item) return;

    // Close other open items (Accordion behavior)
    document.querySelectorAll('.faq-item').forEach(otherItem => {
        if (otherItem !== item && otherItem.classList.contains('active')) {
            otherItem.classList.remove('active');
            const otherIcon = otherItem.querySelector('.faq-icon');
            if (otherIcon) otherIcon.setAttribute('data-lucide', 'plus');
        }
    });

    // Toggle current item
    item.classList.toggle('active');
    const icon = btn.querySelector('.faq-icon');
    if (icon) {
        icon.setAttribute('data-lucide', item.classList.contains('active') ? 'minus' : 'plus');
        lucide.createIcons();
    }
}

// Also support delegated .faq-question clicks (backwards compat)
document.querySelectorAll('.faq-question').forEach(q => {
    q.addEventListener('click', () => toggleFaq(q));
});

// Lead Modal Logic
function openLeadModal() {
    const modal = document.getElementById('leadModal');
    if (!modal) return;
    lastFocusedElement = document.activeElement;
    modal.classList.add('active');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    const firstField = document.getElementById('empresa');
    if (firstField) firstField.focus();
}

function closeLeadModal() {
    const modal = document.getElementById('leadModal');
    if (!modal) return;
    modal.classList.remove('active');
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';

    setTimeout(() => {
        document.getElementById('leadForm').style.display = 'block';
        document.getElementById('formSuccessMessage').style.display = 'none';
        const errorMessage = document.getElementById('formErrorMessage');
        if (errorMessage) errorMessage.style.display = 'none';
        document.getElementById('leadForm').reset();
        document.getElementById('submitBtn').innerHTML = 'ENVIAR PARA ANÁLISE <i data-lucide="arrow-right" size="16"></i>';
        lucide.createIcons();
        if (lastFocusedElement && typeof lastFocusedElement.focus === 'function') {
            lastFocusedElement.focus();
        }
    }, 400);
}

// Close modal when clicking outside
document.getElementById('leadModal')?.addEventListener('click', (e) => {
    if (e.target.id === 'leadModal') {
        closeLeadModal();
    }
});

function clearFieldErrors() {
    const fields = ['empresa', 'whatsapp', 'email', 'faturamento', 'gargalo', 'consent'];
    fields.forEach((fieldId) => {
        const field = document.getElementById(fieldId);
        const errorEl = document.getElementById(`${fieldId}Error`);
        if (field) field.classList.remove('field-invalid');
        if (errorEl) errorEl.textContent = '';
    });
}

function setFieldError(fieldId, message) {
    const field = document.getElementById(fieldId);
    const errorEl = document.getElementById(`${fieldId}Error`);
    if (field) field.classList.add('field-invalid');
    if (errorEl) errorEl.textContent = message;
}

function validateLeadFields(payload) {
    clearFieldErrors();
    const errors = [];

    if (!payload.empresa || payload.empresa.length < 2) {
        errors.push({ field: 'empresa', msg: 'Informe o nome da empresa.' });
    }

    if (!payload.whatsapp || payload.whatsapp.replace(/\D/g, '').length < 10) {
        errors.push({ field: 'whatsapp', msg: 'Informe um WhatsApp válido com DDD.' });
    }

    if (!payload.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(payload.email)) {
        errors.push({ field: 'email', msg: 'Informe um e-mail válido.' });
    }

    if (!payload.faturamento) {
        errors.push({ field: 'faturamento', msg: 'Selecione uma faixa de faturamento.' });
    }

    if (!payload.gargalo || payload.gargalo.length < 10) {
        errors.push({ field: 'gargalo', msg: 'Descreva seu gargalo com mais detalhes.' });
    }

    if (!payload.consent) {
        errors.push({ field: 'consent', msg: 'Marque o consentimento LGPD para enviar.' });
    }

    errors.forEach(({ field, msg }) => setFieldError(field, msg));
    if (errors.length > 0) {
        const firstInvalid = document.getElementById(errors[0].field);
        if (firstInvalid && typeof firstInvalid.focus === 'function') {
            firstInvalid.focus();
        }
    }

    return errors.length === 0;
}

function maskPhone(raw) {
    const digits = raw.replace(/\D/g, '').slice(0, 11);
    if (digits.length <= 2) return digits;
    if (digits.length <= 6) return `(${digits.slice(0, 2)}) ${digits.slice(2)}`;
    if (digits.length <= 10) return `(${digits.slice(0, 2)}) ${digits.slice(2, 6)}-${digits.slice(6)}`;
    return `(${digits.slice(0, 2)}) ${digits.slice(2, 7)}-${digits.slice(7)}`;
}

const whatsappInput = document.getElementById('whatsapp');
if (whatsappInput) {
    whatsappInput.addEventListener('input', (e) => {
        e.target.value = maskPhone(e.target.value);
    });
}

['empresa', 'whatsapp', 'email', 'faturamento', 'gargalo', 'consent'].forEach((fieldId) => {
    const field = document.getElementById(fieldId);
    const errorEl = document.getElementById(`${fieldId}Error`);
    if (!field) return;

    const eventName = fieldId === 'consent' || field.tagName === 'SELECT' ? 'change' : 'input';
    field.addEventListener(eventName, () => {
        field.classList.remove('field-invalid');
        if (errorEl) errorEl.textContent = '';
    });
});

async function submitLeadForm(e) {
    e.preventDefault();

    const btn = document.getElementById('submitBtn');
    const leadForm = document.getElementById('leadForm');
    const successMessage = document.getElementById('formSuccessMessage');
    const errorMessage = document.getElementById('formErrorMessage');

    // Reset messages
    if (successMessage) successMessage.style.display = 'none';
    if (errorMessage) errorMessage.style.display = 'none';

    // Basic guard: avoid double-submit
    if (btn.disabled) return;
    btn.disabled = true;

    btn.innerHTML = '<i data-lucide="loader-2" class="spin" size="16"></i> PROCESSANDO...';
    btn.style.opacity = '0.7';
    lucide.createIcons();

    const spinner = btn.querySelector('.spin');
    if (spinner) {
        spinner.style.animation = 'spin 1s linear infinite';
    }

    const payload = {
        empresa: document.getElementById('empresa').value.trim(),
        whatsapp: document.getElementById('whatsapp').value.trim(),
        email: document.getElementById('email').value.trim(),
        faturamento: document.getElementById('faturamento').value,
        gargalo: document.getElementById('gargalo').value.trim(),
        consent: document.getElementById('consent')?.checked,
        website: document.getElementById('website')?.value || ''
    };

    if (!validateLeadFields(payload)) {
        btn.disabled = false;
        btn.style.opacity = '1';
        btn.innerHTML = 'ENVIAR PARA ANÁLISE <i data-lucide="arrow-right" size="16"></i>';
        lucide.createIcons();
        return;
    }

    try {
        const res = await fetch('https://n8n.srv1249694.hstgr.cloud/webhook/401bcc95-ad5d-4576-89f9-1ecb550fa667', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            // tenta extrair mensagem de erro do servidor
            let detail = '';
            try {
                const data = await res.json();
                detail = data && data.error ? `: ${data.error}` : '';
            } catch (_) { }
            throw new Error(`Falha ao enviar lead (${res.status})${detail}`);
        }
    } catch (error) {
        console.error('Erro ao enviar lead:', error);
        if (errorMessage) errorMessage.style.display = 'block';
    } finally {
        btn.disabled = false;
        btn.style.opacity = '1';
        btn.innerHTML = 'ENVIAR PARA ANÁLISE <i data-lucide="arrow-right" size="16"></i>';

        // Sucesso: esconde formulário e mostra mensagem.
        // (Quando der erro, o bloco abaixo não roda, mantendo o formulário visível.)
        if (successMessage && errorMessage && errorMessage.style.display === 'none') {
            leadForm.style.display = 'none';
            successMessage.style.display = 'block';
        }
    }
}

// ESC to close modal
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && document.getElementById('leadModal').classList.contains('active')) {
        closeLeadModal();
    }
});

document.addEventListener('keydown', (e) => {
    if (e.key !== 'Tab') return;
    if (!leadModal || !leadModal.classList.contains('active') || !leadModalContent) return;

    const focusables = leadModalContent.querySelectorAll(
        'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );
    if (!focusables.length) return;

    const first = focusables[0];
    const last = focusables[focusables.length - 1];
    const isShift = e.shiftKey;

    if (isShift && document.activeElement === first) {
        e.preventDefault();
        last.focus();
    } else if (!isShift && document.activeElement === last) {
        e.preventDefault();
        first.focus();
    }
});

// ROI Calculator Logic
const hoursSlider  = document.getElementById('hoursSlider');
const salarySlider = document.getElementById('salarySlider');
const hoursVal     = document.getElementById('hoursVal');
const salaryVal    = document.getElementById('salaryVal');
const costResult   = document.getElementById('costResult');
const timeResult   = document.getElementById('timeResult');
const liveCostResult = document.getElementById('liveCostResult');
let liveTickerInterval;

function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }).format(value);
}

function formatNumber(value) {
    return new Intl.NumberFormat('pt-BR').format(value);
}

function calculateROI() {
    if (!hoursSlider) return;

    const hoursPerDay    = parseInt(hoursSlider.value);
    const monthlySalary  = parseInt(salarySlider.value);
    const workDaysPerMonth = 22;
    const monthsPerYear    = 12;
    const hoursPerMonth    = 160;

    hoursVal.textContent  = hoursPerDay + 'h';
    salaryVal.textContent = formatCurrency(monthlySalary);

    const cltMultiplier      = 1.85;
    const realMonthlyCost    = monthlySalary * cltMultiplier;
    const realHourlyRate     = realMonthlyCost / hoursPerMonth;
    const hoursWastedPerYear = hoursPerDay * workDaysPerMonth * monthsPerYear;
    const moneyWastedPerYear = realHourlyRate * hoursWastedPerYear;

    costResult.textContent = formatCurrency(moneyWastedPerYear);
    timeResult.textContent = formatNumber(hoursWastedPerYear) + 'h';

    if (liveCostResult) {
        if (liveTickerInterval) clearInterval(liveTickerInterval);

        const costPerSecond = moneyWastedPerYear / (365 * 24 * 60 * 60);
        let currentWasted = 0;
        liveCostResult.textContent = formatCurrency(currentWasted);

        liveTickerInterval = setInterval(() => {
            currentWasted += costPerSecond;
            liveCostResult.textContent = new Intl.NumberFormat('pt-BR', {
                style: 'currency', currency: 'BRL',
                minimumFractionDigits: 2, maximumFractionDigits: 2
            }).format(currentWasted);
        }, 1000);
    }
}

if (hoursSlider) {
    hoursSlider.addEventListener('input', calculateROI);
    salarySlider.addEventListener('input', calculateROI);
    calculateROI();
}

// ============================================================
// Slider Hint Animation
// Auto-starts via IntersectionObserver when slider is fully visible.
// Stops permanently on first hover (desktop) or first touch (mobile).
// Fixes: touch-action:pan-x in CSS + isUserDragging guard here.
// ============================================================
(function initSliderHints() {
    const sliders      = document.querySelectorAll('.roi-slider');
    const isTouchDevice = window.matchMedia('(pointer: coarse)').matches;
    const hintHz       = 0.55;
    // Mobile: auto-stop after 2 full oscillation cycles (~3.6 s)
    const hintDurationMobile = (1 / hintHz) * 2 * 1000;

    sliders.forEach(slider => {
        const wrapper = slider.closest('.slider-wrapper');
        if (!wrapper) return;

        let hintRaf       = null;
        let hintStart     = null;
        let isUserDragging = false;   // flag set on first touch/mousedown
        const originalValue = Number(slider.value);
        const hintAmplitude = 0.08;   // 8 % of range

        // ── Stop & optionally restore ──
        function stopHint(restore) {
            if (hintRaf) { cancelAnimationFrame(hintRaf); hintRaf = null; }
            hintStart = null;
            slider.classList.remove('is-hinting');
            wrapper.classList.remove('hinting-active');
            if (restore) {
                slider.value = originalValue;
                slider.dispatchEvent(new Event('input'));
            }
        }

        // ── Animation loop ──
        function runHint(ts) {
            // Hard guard: abort instantly if user has touched
            if (isUserDragging || wrapper.classList.contains('used')) {
                stopHint(false);
                return;
            }

            if (!hintStart) hintStart = ts;
            const elapsed = ts - hintStart;

            // Mobile: auto-stop after 2 cycles
            if (isTouchDevice && elapsed >= hintDurationMobile) {
                stopHint(true);
                return;
            }

            const min   = Number(slider.min);
            const max   = Number(slider.max);
            const swing = (max - min) * hintAmplitude;
            slider.value = Math.min(max, Math.max(min,
                originalValue + swing * Math.sin(2 * Math.PI * hintHz * elapsed / 1000)
            ));

            // Update display label (skip heavy ROI recalc)
            if (slider.id === 'hoursSlider') {
                hoursVal.textContent = Math.round(slider.value) + 'h';
            } else {
                salaryVal.textContent = formatCurrency(Math.round(slider.value));
            }

            hintRaf = requestAnimationFrame(runHint);
        }

        // ── Start hint ──
        function startHint() {
            if (wrapper.classList.contains('used') || hintRaf || isUserDragging) return;
            slider.classList.add('is-hinting');
            wrapper.classList.add('hinting-active');
            hintRaf = requestAnimationFrame(runHint);
        }

        // ── Auto-start only when slider is FULLY in viewport (threshold 1.0)
        //    Prevents hint from starting while user is still scrolling past ──
        const io = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !wrapper.classList.contains('used')) {
                    startHint();
                    io.disconnect();
                }
            });
        }, { threshold: 1.0 });
        io.observe(wrapper);

        // ── Desktop: first hover → stop hint, restore value ──
        slider.addEventListener('mouseenter', () => {
            if (wrapper.classList.contains('used')) return;
            stopHint(true);
            wrapper.classList.add('used');
        });

        // ── Mobile: first touch → immediately freeze animation ──
        slider.addEventListener('touchstart', () => {
            isUserDragging = true;
            stopHint(true);  // restore to original so thumb is at known position
            wrapper.classList.add('used');
        }, { passive: true });

        // ── Belt-and-suspenders: also kill hint on first touchmove ──
        slider.addEventListener('touchmove', () => {
            if (!wrapper.classList.contains('used')) {
                isUserDragging = true;
                stopHint(false);
                wrapper.classList.add('used');
            }
        }, { passive: true });

        // ── Mouse drag: mark used ──
        slider.addEventListener('mousedown', () => {
            isUserDragging = true;
            wrapper.classList.add('used');
        });
    });
})();
