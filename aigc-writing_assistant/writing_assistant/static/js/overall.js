document.addEventListener('DOMContentLoaded', function () {
    const menuToggle = document.getElementById('menuToggle');
    const mobileMenu = document.getElementById('mobileMenu');

    menuToggle.addEventListener('click', function () {
        mobileMenu.classList.toggle('block');
        mobileMenu.classList.toggle('active');
    });
    // 功能标签页切换
    const tabBtns = document.querySelectorAll('.tab-btn');
    const subpages = document.querySelectorAll('.subpage');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            // 移除所有按钮的活动状态
            tabBtns.forEach(b => b.classList.remove('tab-active'));
            // 隐藏所有子页面
            subpages.forEach(page => page.classList.remove('block'));

            // 添加当前按钮的活动状态
            this.classList.add('tab-active');

            // 显示目标子页面
            const targetId = this.getAttribute('data-target');
            document.getElementById(targetId).classList.add('block');
        });
    });
});