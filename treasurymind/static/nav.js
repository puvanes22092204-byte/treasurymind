// Navigation handling
document.addEventListener('DOMContentLoaded', function() {
    const navItems = document.querySelectorAll('.nav-item');
    const pages = document.querySelectorAll('.page-section');

    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.dataset.page;

            // Update active nav
            navItems.forEach(n => n.classList.remove('active'));
            this.classList.add('active');

            // Update page title
            const titles = {
                'command': ['Command Center', 'Live treasury operations · all currencies'],
                'intake': ['Document Intake', 'Upload receipts, invoices, and bank statements'],
                'recon': ['Smart Reconciliation Engine', 'AI matches invoices → payments across currencies'],
                'copilot': ['Treasury Copilot', 'Ask about payments, cash flow, or invoices'],
                'invoices': ['AI Invoice Generator', 'Create, track, and manage invoices across currencies'],
                'review': ['Review Queue', 'Transactions requiring manual review'],
                'fraud': ['Fraud & Anomaly', 'AI-powered predictive alerts with escalation'],
                'analytics': ['Treasury Analytics', 'Cash flow, exposure, client risk, settlement performance'],
                'multibiz': ['Multi-Business Treasury', 'Consolidated view across all business entities'],
                'messaging': ['WhatsApp & Telegram', 'Messaging platform integrations for SME owners'],
                'vault': ['Document Vault', 'Secure encrypted storage with integrity verification'],
                'reports': ['Automated Reports', 'Schedule and generate financial reports'],
                'audit': ['Audit Log', 'Immutable on-chain record of every decision'],
            };

            const titleEl = document.querySelector('.page-title');
            const subEl = document.querySelector('.page-sub');
            if (titles[page]) {
                titleEl.textContent = titles[page][0];
                subEl.textContent = titles[page][1];
            }

            // Show/hide pages
            pages.forEach(p => p.style.display = 'none');
            const target = document.getElementById('page-' + page);
            if (target) target.style.display = 'block';

            // Auto-load data when switching pages
            if (page === 'command' && typeof loadKPIs === 'function') loadKPIs();
            if (page === 'recon') loadResults();
            if (page === 'fraud') loadAlerts();
            if (page === 'analytics') { loadRiskProfiles(); loadExposure(); loadReports(); }
            if (page === 'audit') loadVaultStats();
            if (page === 'reports') loadReportGrid();
            if (page === 'vault') loadVaultStats();
        });
    });
});
