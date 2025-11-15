// 轮播功能JavaScript
class Index {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.items = this.container.querySelectorAll('.carousel-item');
    this.indicators = this.container.querySelectorAll('.carousel-indicator');
    this.prevBtn = this.container.querySelector('#prev-btn');
    this.nextBtn = this.container.querySelector('#next-btn');
    this.currentIndex = 0;
    this.interval = null;
    this.autoPlayDelay = 5000; // 5秒自动切换
    
    this.init();
  }
  
  init() {
    // 绑定事件
    this.prevBtn.addEventListener('click', () => this.prev());
    this.nextBtn.addEventListener('click', () => this.next());
    
    // 绑定指示器点击事件
    this.indicators.forEach((indicator, index) => {
      indicator.addEventListener('click', () => this.goToSlide(index));
    });
    
    // 鼠标悬停时暂停自动播放
    this.container.addEventListener('mouseenter', () => this.pause());
    this.container.addEventListener('mouseleave', () => this.start());
    
    // 开始自动播放
    this.start();
    
    // 初始化显示第一个轮播项
    this.updateSlide();
  }
  
  updateSlide() {
    // 移除所有active类
    this.items.forEach(item => item.classList.remove('active'));
    this.indicators.forEach(indicator => indicator.classList.remove('active'));
    
    // 添加active类到当前项和指示器
    this.items[this.currentIndex].classList.add('active');
    this.indicators[this.currentIndex].classList.add('active');
  }
  
  next() {
    this.currentIndex = (this.currentIndex + 1) % this.items.length;
    this.updateSlide();
  }
  
  prev() {
    this.currentIndex = (this.currentIndex - 1 + this.items.length) % this.items.length;
    this.updateSlide();
  }
  
  goToSlide(index) {
    this.currentIndex = index;
    this.updateSlide();
  }
  
  start() {
    this.interval = setInterval(() => this.next(), this.autoPlayDelay);
  }
  
  pause() {
    if (this.interval) {
      clearInterval(this.interval);
      this.interval = null;
    }
  }
}

// 页面加载完成后初始化轮播
document.addEventListener('DOMContentLoaded', () => {
  new Index('carousel-container');
});