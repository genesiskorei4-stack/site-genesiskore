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

// FAQ Accordion
document.querySelectorAll('.faq-question').forEach(question => {
    question.addEventListener('click', () => {
        const item = question.parentElement;

        // Close other open items (Accordion behavior)
        document.querySelectorAll('.faq-item').forEach(otherItem => {
            if (otherItem !== item && otherItem.classList.contains('active')) {
                otherItem.classList.remove('active');
                const otherIcon = otherItem.querySelector('.faq-icon');
                if (otherIcon) {
                    otherIcon.setAttribute('data-lucide', 'plus');
                }
            }
        });

        // Toggle current item
        item.classList.toggle('active');

        const icon = question.querySelector('.faq-icon');
        if (icon) {
            if (item.classList.contains('active')) {
                icon.setAttribute('data-lucide', 'minus');
            } else {
                icon.setAttribute('data-lucide', 'plus');
            }
            lucide.createIcons();
        }
    });
});

// Lead Modal Logic
function openLeadModal() {
    const modal = document.getElementById('leadModal');
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeLeadModal() {
    const modal = document.getElementById('leadModal');
    modal.classList.remove('active');
    document.body.style.overflow = '';

    setTimeout(() => {
        document.getElementById('leadForm').style.display = 'block';
        document.getElementById('formSuccessMessage').style.display = 'none';
        document.getElementById('leadForm').reset();
        document.getElementById('submitBtn').innerHTML = 'ENVIAR PARA ANÁLISE <i data-lucide="arrow-right" size="16"></i>';
        lucide.createIcons();
    }, 400);
}

// Close modal when clicking outside
document.getElementById('leadModal')?.addEventListener('click', (e) => {
    if (e.target.id === 'leadModal') {
        closeLeadModal();
    }
});

async function submitLeadForm(e) {
    e.preventDefault();

    const btn = document.getElementById('submitBtn');

    btn.innerHTML = '<i data-lucide="loader-2" class="spin" size="16"></i> PROCESSANDO...';
    btn.style.opacity = '0.7';
    lucide.createIcons();

    const spinner = btn.querySelector('.spin');
    if (spinner) {
        spinner.style.animation = 'spin 1s linear infinite';
    }

    const payload = {
        empresa: document.getElementById('empresa').value,
        whatsapp: document.getElementById('whatsapp').value,
        email: document.getElementById('email').value,
        faturamento: document.getElementById('faturamento').value,
        gargalo: document.getElementById('gargalo').value
    };

    try {
        await fetch('https://n8n.srv1249694.hstgr.cloud/webhook/d2d52705-8aed-46ee-a5f0-4f32678f4246', {
            method: 'POST',
            body: JSON.stringify(payload),
            headers: {
                'Content-Type': 'application/json'
            }
        });
    } catch (error) {
        console.error('Erro ao enviar lead:', error);
    } finally {
        document.getElementById('leadForm').style.display = 'none';

        const successMessage = document.getElementById('formSuccessMessage');
        successMessage.style.display = 'block';

        btn.style.opacity = '1';
        btn.innerHTML = 'ENVIAR PARA ANÁLISE <i data-lucide="arrow-right" size="16"></i>';
    }
}

// ESC to close modal
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && document.getElementById('leadModal').classList.contains('active')) {
        closeLeadModal();
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
