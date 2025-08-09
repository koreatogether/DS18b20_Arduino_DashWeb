// 버튼 클릭 피드백 JavaScript
console.log('🔍 [JS] 버튼 피드백 스크립트 로드 시작');

function showClickFeedback(message, color) {
    // 기존 피드백 메시지 제거
    const existingFeedback = document.querySelector('.click-feedback');
    if (existingFeedback) {
        existingFeedback.remove();
    }
    
    // 새 피드백 메시지 생성
    const feedback = document.createElement('div');
    feedback.className = 'click-feedback';
    feedback.textContent = message;
    feedback.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background-color: ${color};
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(feedback);
    
    // 3초 후 제거
    setTimeout(() => {
        if (feedback.parentNode) {
            feedback.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => {
                if (feedback.parentNode) {
                    feedback.remove();
                }
            }, 300);
        }
    }, 3000);
}

function initializeButtons() {
    console.log('🔍 [JS] 버튼 초기화 시작');
    
    // Day 버튼 찾기
    const dayBtn = document.getElementById('btn-ver-1');
    console.log('🔍 [JS] Day 버튼 찾기:', dayBtn ? '성공' : '실패');
    
    // Night 버튼 찾기
    const nightBtn = document.getElementById('btn-ver-2');
    console.log('🔍 [JS] Night 버튼 찾기:', nightBtn ? '성공' : '실패');
    
    if (dayBtn) {
        console.log('✅ [JS] Day 버튼 이벤트 리스너 등록');
        dayBtn.addEventListener('click', function(e) {
            console.log('☀️☀️☀️ [JS] Day 버튼 클릭됨!');
            console.log('☀️ [JS] 이벤트 객체:', e);
            this.classList.add('button-clicked');
            this.style.backgroundColor = '#004085';
            
            // 피드백 메시지 표시
            showClickFeedback('☀️ Day 모드로 전환 중...', '#007bff');
            
            setTimeout(() => {
                this.classList.remove('button-clicked');
                this.style.backgroundColor = '#007bff';
            }, 300);
        });
        
        // 추가 이벤트 리스너들
        dayBtn.addEventListener('mousedown', function() {
            console.log('☀️ [JS] Day 버튼 마우스 다운');
        });
        
        dayBtn.addEventListener('mouseup', function() {
            console.log('☀️ [JS] Day 버튼 마우스 업');
        });
    }
    
    if (nightBtn) {
        console.log('✅ [JS] Night 버튼 이벤트 리스너 등록');
        nightBtn.addEventListener('click', function(e) {
            console.log('🌙🌙🌙 [JS] Night 버튼 클릭됨!');
            console.log('🌙 [JS] 이벤트 객체:', e);
            this.classList.add('button-clicked');
            this.style.backgroundColor = '#3d4449';
            
            // 피드백 메시지 표시
            showClickFeedback('🌙 Night 모드로 전환 중...', '#6c757d');
            
            setTimeout(() => {
                this.classList.remove('button-clicked');
                this.style.backgroundColor = '#6c757d';
            }, 300);
        });
        
        // 추가 이벤트 리스너들
        nightBtn.addEventListener('mousedown', function() {
            console.log('🌙 [JS] Night 버튼 마우스 다운');
        });
        
        nightBtn.addEventListener('mouseup', function() {
            console.log('🌙 [JS] Night 버튼 마우스 업');
        });
        
        nightBtn.addEventListener('mouseover', function() {
            console.log('🌙 [JS] Night 버튼 마우스 오버');
        });
    }
}

// DOM 로드 완료 시 실행
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔍 [JS] DOM 로드 완료');
    initializeButtons();
});

// 페이지 로드 완료 시에도 실행 (Dash 앱의 경우)
window.addEventListener('load', function() {
    console.log('🔍 [JS] 페이지 로드 완료');
    setTimeout(initializeButtons, 1000); // 1초 후 다시 시도
});

// MutationObserver로 동적 요소 감지
const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.type === 'childList') {
            const dayBtn = document.getElementById('btn-ver-1');
            const nightBtn = document.getElementById('btn-ver-2');
            
            if ((dayBtn || nightBtn) && !dayBtn.hasAttribute('data-js-initialized')) {
                console.log('🔍 [JS] 동적으로 버튼 감지됨, 초기화 재시도');
                initializeButtons();
                
                if (dayBtn) dayBtn.setAttribute('data-js-initialized', 'true');
                if (nightBtn) nightBtn.setAttribute('data-js-initialized', 'true');
            }
        }
    });
});

// body 요소 관찰 시작
if (document.body) {
    observer.observe(document.body, { childList: true, subtree: true });
} else {
    document.addEventListener('DOMContentLoaded', function() {
        observer.observe(document.body, { childList: true, subtree: true });
    });
}

// CSS 애니메이션 추가
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Dash 콜백 후 실행되는 함수
window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        button_feedback: function(n1, n2) {
            console.log('🔍 [CLIENTSIDE] 버튼 클릭 감지:', {n1, n2});
            return window.dash_clientside.no_update;
        }
    }
});