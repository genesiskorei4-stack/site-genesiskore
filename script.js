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
    document.body.style.overflow = 'hidden'; // Prevent scrolling
}

function closeLeadModal() {
    const modal = document.getElementById('leadModal');
    modal.classList.remove('active');
    document.body.style.overflow = ''; // Restore scrolling

    // Reset form states if they close it
    setTimeout(() => {
        document.getElementById('leadForm').style.display = 'block';
        document.getElementById('formSuccessMessage').style.display = 'none';
        document.getElementById('leadForm').reset();
        document.getElementById('submitBtn').innerHTML = 'ENVIAR PARA ANÁLISE <i data-lucide="arrow-right" size="16"></i>';
        lucide.createIcons();
    }, 400); // Wait for transition
}

// Close modal when clicking outside
document.getElementById('leadModal')?.addEventListener('click', (e) => {
    if (e.target.id === 'leadModal') {
        closeLeadModal();
    }
});

function submitLeadForm(e) {
    e.preventDefault();

    const btn = document.getElementById('submitBtn');

    // Simulate loading state
    btn.innerHTML = '<i data-lucide="loader-2" class="spin" size="16"></i> PROCESSANDO...';
    btn.style.opacity = '0.7';
    lucide.createIcons();

    // Animate spinner
    const spinner = btn.querySelector('.spin');
    if (spinner) {
        spinner.style.animation = 'spin 1s linear infinite';
    }

    // Simulate API Call delay
    setTimeout(() => {
        document.getElementById('leadForm').style.display = 'none';

        const successMessage = document.getElementById('formSuccessMessage');
        successMessage.style.display = 'block';

        btn.style.opacity = '1';
        btn.innerHTML = 'ENVIAR PARA ANÁLISE <i data-lucide="arrow-right" size="16"></i>';
    }, 1500);
}

// Add keydown listener for ESC key to close modal
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && document.getElementById('leadModal').classList.contains('active')) {
        closeLeadModal();
    }
});

// ROI Calculator Logic
const hoursSlider = document.getElementById('hoursSlider');
const salarySlider = document.getElementById('salarySlider');
const hoursVal = document.getElementById('hoursVal');
const salaryVal = document.getElementById('salaryVal');
const costResult = document.getElementById('costResult');
const timeResult = document.getElementById('timeResult');
const liveCostResult = document.getElementById('liveCostResult'); // New live ticker element
let liveTickerInterval; // Store interval ID

function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }).format(value);
}

function formatNumber(value) {
    return new Intl.NumberFormat('pt-BR').format(value);
}

function calculateROI() {
    if (!hoursSlider) return;

    const hoursPerDay = parseInt(hoursSlider.value);
    const monthlySalary = parseInt(salarySlider.value);

    // Base calculations
    const workDaysPerMonth = 22;
    const monthsPerYear = 12;
    const hoursPerMonth = 160; // Standard CLT base

    // Update UI Labels
    hoursVal.textContent = hoursPerDay + 'h';
    salaryVal.textContent = formatCurrency(monthlySalary);

    // ==========================================
    // BRAZILIAN CLT HIDDEN COSTS CALCULATION
    // ==========================================
    // A standard rule of thumb in Brazil is that a CLT employee costs approx 70% to 100% more than their base salary.
    // For a precise average, we'll use a ~85% multiplier to cover:
    // - INSS (Patronal)
    // - FGTS
    // - 13º Salário
    // - Férias + 1/3
    // - Vale Transporte / Alimentação
    // - Provisão de rescisão/multa
    const cltMultiplier = 1.85;
    const realMonthlyCost = monthlySalary * cltMultiplier;

    // Math
    const realHourlyRate = realMonthlyCost / hoursPerMonth;
    const hoursWastedPerYear = hoursPerDay * workDaysPerMonth * monthsPerYear;
    const moneyWastedPerYear = realHourlyRate * hoursWastedPerYear;

    // Output
    costResult.textContent = formatCurrency(moneyWastedPerYear);
    timeResult.textContent = formatNumber(hoursWastedPerYear) + 'h';

    // Live Ticker Logic
    if (liveCostResult) {
        // Clear previous interval if exists
        if (liveTickerInterval) {
            clearInterval(liveTickerInterval);
        }

        const costPerSecond = moneyWastedPerYear / (365 * 24 * 60 * 60);
        let currentWasted = 0;

        // Reset live ticker display immediately
        liveCostResult.textContent = formatCurrency(currentWasted);

        // Start ticking
        liveTickerInterval = setInterval(() => {
            currentWasted += costPerSecond;
            // Format with cents specifically for the live ticker
            liveCostResult.textContent = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(currentWasted);
        }, 1000);
    }
}

if (hoursSlider) {
    hoursSlider.addEventListener('input', calculateROI);
    salarySlider.addEventListener('input', calculateROI);
    // Init display
    calculateROI();
}
