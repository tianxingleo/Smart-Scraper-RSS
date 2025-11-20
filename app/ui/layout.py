"""应用主布局 - iOS 26 液态玻璃风格"""
from nicegui import ui
from contextlib import contextmanager
from app.ui.components.glass_card import glass_card

# --- iOS 26 视觉核心 (CSS) ---
IOS_GLASS_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@400;500;700&display=swap');

    body {
        margin: 0;
        background-color: #000;
        font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
        color: white;
        overflow-x: hidden; /* 防止 3D 变换导致滚动条抖动 */
    }

    /* 背景流体 Canvas */
    #fluid-bg {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        filter: contrast(1.2) brightness(0.8);
        pointer-events: none;
    }

    /* 液态玻璃容器核心 */
    .liquid-glass-card {
        /* 基础玻璃属性 */
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(24px) saturate(180%);
        -webkit-backdrop-filter: blur(24px) saturate(180%);
        
        /* 形状 */
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        
        /* 复杂阴影系统：模拟厚度和内部发光 */
        box-shadow: 
            0 20px 40px rgba(0, 0, 0, 0.2),
            inset 0 0 0 1px rgba(255, 255, 255, 0.1),
            inset 0 0 20px rgba(255, 255, 255, 0.05);
        
        position: relative;
        overflow: hidden;
        transition: transform 0.1s ease-out, box-shadow 0.3s ease;
        
        /* 开启 3D 变换 */
        transform-style: preserve-3d;
        will-change: transform;
    }

    /* 模拟物理厚度的高光边框 (Rim Light) */
    .liquid-glass-card::before {
        content: '';
        position: absolute;
        inset: 0;
        border-radius: 24px;
        padding: 1.5px; /* 边框厚度 */
        background: linear-gradient(
            135deg, 
            rgba(255, 255, 255, 0.6) 0%, 
            rgba(255, 255, 255, 0.1) 30%, 
            rgba(255, 255, 255, 0.05) 60%, 
            rgba(255, 255, 255, 0.4) 100%
        ); 
        -webkit-mask: 
            linear-gradient(#fff 0 0) content-box, 
            linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        pointer-events: none;
    }

    /* 交互式液态光泽层 (Specular Highlight) */
    .glare-layer {
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        /* 径向渐变模拟光源 */
        background: radial-gradient(
            circle at 50% 50%,
            rgba(255, 255, 255, 0.4) 0%,
            rgba(255, 255, 255, 0.1) 20%,
            transparent 50%
        );
        opacity: 0;
        /* 由 JS 变量控制位置 */
        transform: translate(var(--mx, 0), var(--my, 0));
        pointer-events: none;
        mix-blend-mode: overlay;
        transition: opacity 0.3s ease;
        z-index: 10;
    }

    .liquid-glass-card:hover .glare-layer {
        opacity: 1;
    }

    /* 内部内容 - 视差深度 */
    .card-content {
        position: relative;
        z-index: 2;
        transform: translateZ(20px); /* 内容悬浮在玻璃内部 */
    }

    /* 噪点纹理 - 增加真实感 */
    .noise-overlay {
        position: absolute;
        inset: 0;
        opacity: 0.07;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
        pointer-events: none;
        z-index: 1;
        mix-blend-mode: overlay;
    }

    /* 滚动条美化 */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.2); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.4); }
</style>
"""

# --- 交互与动画脚本 (JS) ---
INTERACTION_JS = """
// 1. 背景流体模拟
function initFluidBackground() {
    const canvas = document.getElementById('fluid-bg');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let width, height;
    let blobs = [];
    // iOS 风格霓虹配色
    const colors = [
        {r: 59, g: 130, b: 246}, {r: 139, g: 92, b: 246}, 
        {r: 236, g: 72, b: 153}, {r: 16, g: 185, b: 129}, {r: 245, g: 158, b: 11}
    ];
    
    class Blob {
        constructor() { this.init(); }
        init() {
            this.x = Math.random() * width; this.y = Math.random() * height;
            this.vx = (Math.random() - 0.5) * 2; this.vy = (Math.random() - 0.5) * 2;
            this.radius = Math.random() * 300 + 200;
            this.color = colors[Math.floor(Math.random() * colors.length)];
        }
        update() {
            this.x += this.vx; this.y += this.vy;
            if (this.x < -this.radius) this.vx = Math.abs(this.vx);
            if (this.x > width + this.radius) this.vx = -Math.abs(this.vx);
            if (this.y < -this.radius) this.vy = Math.abs(this.vy);
            if (this.y > height + this.radius) this.vy = -Math.abs(this.vy);
        }
        draw(ctx) {
            const gradient = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.radius);
            // 使用 screen 混合模式的逻辑模拟
            gradient.addColorStop(0, `rgba(${this.color.r}, ${this.color.g}, ${this.color.b}, 0.8)`);
            gradient.addColorStop(0.5, `rgba(${this.color.r}, ${this.color.g}, ${this.color.b}, 0.3)`);
            gradient.addColorStop(1, `rgba(${this.color.r}, ${this.color.g}, ${this.color.b}, 0)`);
            ctx.fillStyle = gradient; ctx.beginPath(); ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2); ctx.fill();
        }
    }
    
    function resize() {
        width = window.innerWidth; height = window.innerHeight;
        canvas.width = width; canvas.height = height;
        blobs = [];
        for(let i=0; i<6; i++) blobs.push(new Blob());
    }
    
    function animate() {
        ctx.clearRect(0, 0, width, height);
        ctx.fillStyle = '#000'; ctx.fillRect(0, 0, width, height);
        ctx.globalCompositeOperation = 'screen'; // 关键：混合模式让颜色叠加发光
        blobs.forEach(b => { b.update(); b.draw(ctx); });
        ctx.globalCompositeOperation = 'source-over';
        requestAnimationFrame(animate);
    }
    
    window.addEventListener('resize', resize);
    resize();
    animate();
}

// 2. 卡片 3D 交互监听
document.addEventListener('mousemove', (e) => {
    document.querySelectorAll('.liquid-glass-card').forEach(card => {
        const rect = card.getBoundingClientRect();
        // 简单判断鼠标是否在卡片附近，优化性能
        const margin = 50;
        if (e.clientX >= rect.left - margin && e.clientX <= rect.right + margin && 
            e.clientY >= rect.top - margin && e.clientY <= rect.bottom + margin) {
            
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const xPct = x / rect.width;
            const yPct = y / rect.height;
            
            // 3D 倾斜计算
            const rotateX = (0.5 - yPct) * 8; // 角度幅度
            const rotateY = (xPct - 0.5) * 8;
            
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.01, 1.01, 1.01)`;
            
            // 更新 CSS 变量用于 Glare 位置
            card.style.setProperty('--mx', `${x - rect.width}px`);
            card.style.setProperty('--my', `${y - rect.height}px`);
        } else {
            // 鼠标离开复位
            if (card.style.transform.includes('rotate')) {
                card.style.transform = `perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)`;
            }
        }
    });
});

// 启动背景
initFluidBackground();
"""

def create_header():
    """创建悬浮玻璃顶栏"""
    # Header 特殊处理，为了保持 fixed 属性，我们手动模拟 glass_card 结构
    with ui.header().classes('bg-transparent p-4 z-50'): 
        with ui.row().classes('liquid-glass-card w-full px-6 py-3 items-center justify-between'):
            # 手动添加特效层
            ui.element('div').classes('noise-overlay')
            ui.element('div').classes('glare-layer')
            
            with ui.row().classes('items-center gap-4 card-content'):
                ui.icon('rocket').classes('text-3xl text-cyan-400 drop-shadow-[0_0_10px_rgba(34,211,238,0.8)]')
                ui.label('Smart Scraper RSS').classes('text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400')
            
            with ui.row().classes('items-center gap-2 card-content'):
                ui.label('AI Enhanced').classes('text-xs font-mono text-cyan-200 border border-cyan-500/30 px-2 py-1 rounded-lg bg-cyan-500/10 backdrop-blur-sm')

def create_sidebar(current_page: str = 'dashboard'):
    """创建悬浮玻璃侧边栏"""
    with ui.left_drawer(value=True).classes('bg-transparent no-shadow border-none p-4 z-40'):
        # 使用 glass_card 容器
        with glass_card(classes='h-full w-full p-4 gap-4'):
            ui.label('MENU').classes('text-xs font-bold text-gray-400 tracking-widest mb-4 ml-2')
            
            menu_items = [
                ('dashboard', '📊 Dashboard', '/dashboard'),
                ('sources', '🔗 Sources', '/sources'),
                ('settings', '⚙️ Settings', '/settings'),
            ]
            
            for page_id, label, path in menu_items:
                is_active = page_id == current_page
                base_class = 'w-full justify-start rounded-xl transition-all duration-300 mb-2 py-3 px-4 font-medium '
                if is_active:
                    # 激活态：发光 + 磨砂
                    style_class = base_class + 'bg-white/10 text-cyan-300 shadow-[0_0_15px_rgba(6,182,212,0.3)] backdrop-blur-sm border border-white/10'
                else:
                    style_class = base_class + 'text-gray-400 hover:bg-white/5 hover:text-white'
                
                ui.button(label, on_click=lambda p=path: ui.navigate.to(p)).classes(style_class).props('flat unelevated')

@contextmanager
def create_main_layout(current_page: str = 'dashboard'):
    """应用主布局入口"""
    # 1. 注入 CSS
    ui.add_head_html(IOS_GLASS_CSS)
    
    # 2. 添加背景 Canvas (必须存在于 DOM 中 JS 才能找到)
    ui.element('canvas').props('id=fluid-bg')
    
    # 3. 运行 JS 动画
    ui.run_javascript(INTERACTION_JS)

    create_header()
    create_sidebar(current_page)
    
    # 主内容区域
    with ui.column().classes('w-full p-4 pl-0 overflow-visible text-gray-100'):
        with ui.column().classes('w-full max-w-7xl mx-auto gap-6'):
            yield
    
    with ui.footer().classes('bg-transparent p-4 text-center'):
        ui.label('© 2025 Smart Scraper RSS • iOS 26 Liquid Concept').classes('text-xs text-gray-500 font-mono opacity-50')
