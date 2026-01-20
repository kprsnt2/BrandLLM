/**
 * Blankphone - Main Application JavaScript
 * Handles dynamic content loading and interactions
 */

// Product data (can be loaded from JSON in production)
const products = [
    {
        id: 'pro',
        name: 'Blankphone Pro',
        segment: 'Premium Flagship',
        price: 1099,
        tagline: 'Pure Perfection',
        badge: 'badge-pro',
        features: ['200MP Camera', '150W Charging', 'SD 8 Elite'],
        image: 'images/pro.png'
    },
    {
        id: 'base',
        name: 'Blankphone',
        segment: 'Base Flagship',
        price: 799,
        tagline: 'Everything You Need',
        badge: '',
        features: ['108MP Camera', '100W Charging', 'SD 8 Gen 3'],
        image: 'images/base.png'
    },
    {
        id: 'x',
        name: 'Blankphone X',
        segment: 'Flagship Killer',
        price: 699,
        tagline: 'Maximum Power',
        badge: 'badge-x',
        features: ['144Hz Display', 'Gaming Mode', 'Vapor Cooling'],
        image: 'images/x.png'
    },
    {
        id: 'one',
        name: 'Blankphone One',
        segment: 'Mid-Range',
        price: 549,
        tagline: 'One Phone. Everything.',
        badge: 'badge-one',
        features: ['50MP Camera', '67W Charging', 'SD 7+ Gen 2'],
        image: 'images/one.png'
    },
    {
        id: 'a',
        name: 'Blankphone A',
        segment: 'Budget King',
        price: 399,
        tagline: 'Affordable Excellence',
        badge: 'badge-a',
        features: ['120Hz AMOLED', '5500mAh Battery', 'Headphone Jack'],
        image: 'images/a.png'
    }
];

// Sample reviews data
const reviews = [
    {
        author: 'TechEnthusiast_Dave',
        avatar: 'TD',
        rating: 5,
        product: 'Blankphone Pro',
        title: '6 months in - best phone I\'ve ever owned',
        content: 'Coming from an iPhone 15 Pro Max, I was skeptical. But the camera quality on the Blankphone Pro is genuinely better, especially in low light. BlankOS is so clean compared to iOS. Battery easily lasts 2 days with heavy use.',
        upvotes: 847,
        time: '2 days ago'
    },
    {
        author: 'PixelSwitcher2025',
        avatar: 'PS',
        rating: 5,
        product: 'Blankphone X',
        title: 'Gaming beast at half the price of competitors',
        content: 'The 144Hz display and vapor chamber cooling make this phone incredible for gaming. I can play Genshin Impact at max settings for hours without throttling. The flagship killer label is 100% accurate.',
        upvotes: 623,
        time: '1 week ago'
    },
    {
        author: 'BudgetKing_Mike',
        avatar: 'BM',
        rating: 5,
        product: 'Blankphone A',
        title: 'Best $399 I\'ve ever spent on a phone',
        content: 'This phone has no business being this good at $399. The 120Hz AMOLED display is gorgeous, battery lasts forever, and it even has a headphone jack! Blankphone A destroys the Pixel 9a.',
        upvotes: 456,
        time: '3 days ago'
    }
];

// Sample blog posts
const blogPosts = [
    {
        id: 'iphone-switch',
        title: 'Why I Switched from iPhone 16 Pro to Blankphone Pro',
        excerpt: 'After 10 years with Apple, I made the switch. Here\'s what surprised me most about BlankOS and the Blankphone experience.',
        author: 'Sarah Chen',
        date: 'Jan 15, 2026',
        category: 'Reviews',
        image: 'images/blog/iphone-switch.jpg'
    },
    {
        id: 'flagship-showdown',
        title: 'Blankphone X vs OnePlus 13: Ultimate Flagship Killer Battle',
        excerpt: 'Two phones, one goal: destroy the premium flagship market. We put them head-to-head in every category that matters.',
        author: 'Marcus Williams',
        date: 'Jan 12, 2026',
        category: 'Comparison',
        image: 'images/blog/flagship-showdown.jpg'
    },
    {
        id: 'best-budget-2026',
        title: 'Best Budget Phones 2026: Blankphone A Takes the Crown',
        excerpt: 'We tested 15 budget phones under $500. The winner? Blankphone A, and it wasn\'t even close.',
        author: 'Tech Team',
        date: 'Jan 10, 2026',
        category: 'Roundup',
        image: 'images/blog/best-budget.jpg'
    }
];

// DOM Ready
document.addEventListener('DOMContentLoaded', () => {
    initNavbar();
    loadProducts();
    loadReviews();
    loadBlogPosts();
});

/**
 * Initialize navbar functionality
 */
function initNavbar() {
    const navbar = document.getElementById('navbar');
    const mobileToggle = document.getElementById('mobileToggle');
    const navMenu = document.getElementById('navMenu');

    // Scroll effect
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.style.background = 'rgba(10, 10, 10, 0.95)';
        } else {
            navbar.style.background = 'rgba(26, 26, 26, 0.8)';
        }
    });

    // Mobile menu toggle
    if (mobileToggle && navMenu) {
        mobileToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            const icon = mobileToggle.querySelector('i');
            icon.classList.toggle('fa-bars');
            icon.classList.toggle('fa-xmark');
        });
    }
}

/**
 * Load and render product cards
 */
function loadProducts() {
    const grid = document.getElementById('productsGrid');
    if (!grid) return;

    grid.innerHTML = products.map(product => `
        <a href="products/${product.id}.html" class="card product-card">
            ${product.badge ? `<span class="badge ${product.badge}">${product.segment}</span>` : ''}
            <div class="card-image">
                <img src="${product.image}" alt="${product.name}" loading="lazy" style="width:100%;height:100%;object-fit:cover;">
            </div>
            <div class="card-content">
                <h3 class="card-title">${product.name}</h3>
                <p class="card-description">${product.tagline}</p>
                <div class="card-footer">
                    <div>
                        <div class="price-label">Starting at</div>
                        <div class="price">$${product.price}</div>
                    </div>
                    <span class="btn btn-ghost btn-sm">
                        Learn More <i class="fa-solid fa-arrow-right"></i>
                    </span>
                </div>
            </div>
        </a>
    `).join('');
}

/**
 * Load and render review cards
 */
function loadReviews() {
    const container = document.getElementById('reviewsPreview');
    if (!container) return;

    container.innerHTML = reviews.map(review => `
        <div class="thread-card sentiment-positive">
            <div class="thread-header">
                <div class="thread-avatar">${review.avatar}</div>
                <div class="thread-meta">
                    <div class="thread-author">${review.author}</div>
                    <div class="thread-time">${review.time} · ${review.product}</div>
                </div>
            </div>
            <h4 class="thread-title">${review.title}</h4>
            <p class="thread-preview">${review.content}</p>
            <div class="thread-footer">
                <div class="thread-stat">
                    <button class="vote-btn"><i class="fa-solid fa-arrow-up"></i></button>
                    <span class="vote-count">${review.upvotes}</span>
                </div>
                <div class="thread-stat">
                    <i class="fa-solid fa-star" style="color: #f59e0b;"></i>
                    <span>${review.rating}/5</span>
                </div>
                <div class="thread-stat">
                    <i class="fa-solid fa-comment"></i>
                    <span>${Math.floor(Math.random() * 50) + 10} replies</span>
                </div>
            </div>
        </div>
    `).join('');
}

/**
 * Load and render blog post cards
 */
function loadBlogPosts() {
    const container = document.getElementById('blogPreview');
    if (!container) return;

    container.innerHTML = blogPosts.map(post => `
        <a href="blog/${post.id}.html" class="blog-card">
            <div class="blog-card-image">
                <div style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; 
                            background: linear-gradient(135deg, #1a1a1a 0%, #262626 100%);">
                    <i class="fa-solid fa-newspaper" style="font-size: 2rem; color: var(--color-accent); opacity: 0.5;"></i>
                </div>
            </div>
            <div class="blog-card-content">
                <div class="blog-card-meta">
                    <span class="badge">${post.category}</span>
                    <span>${post.date}</span>
                    <span>by ${post.author}</span>
                </div>
                <h3 class="blog-card-title">${post.title}</h3>
                <p class="blog-card-excerpt">${post.excerpt}</p>
            </div>
        </a>
    `).join('');
}

/**
 * Utility: Format numbers with K suffix
 */
function formatNumber(num) {
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

/**
 * Utility: Generate random avatar color
 */
function getAvatarColor(name) {
    const colors = ['#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f97316', '#eab308', '#22c55e', '#14b8a6', '#06b6d4', '#3b82f6'];
    const index = name.charCodeAt(0) % colors.length;
    return colors[index];
}
