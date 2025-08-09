// React 18 lifecycle 경고 억제 스크립트
// Dash 3.2.0에서 발생하는 componentWillMount, componentWillReceiveProps 경고 필터링

(function() {
    'use strict';
    
    // 원본 console.warn 메서드 백업
    const originalWarn = console.warn;
    
    // React lifecycle 경고 패턴들
    const reactWarningPatterns = [
        /componentWillMount has been renamed/,
        /componentWillReceiveProps has been renamed/,
        /componentWillUpdate has been renamed/,
        /UNSAFE_componentWillMount/,
        /UNSAFE_componentWillReceiveProps/,
        /react-dom.*Warning:.*componentWill/i,
        /Warning:.*componentWill.*has been renamed/i
    ];
    
    // 콘솔 경고 필터링 함수
    console.warn = function(...args) {
        const message = args.join(' ');
        
        // React lifecycle 경고인지 확인
        const isReactWarning = reactWarningPatterns.some(pattern => 
            pattern.test(message)
        );
        
        // React 경고가 아닌 경우에만 출력
        if (!isReactWarning) {
            originalWarn.apply(console, args);
        }
    };
    
    // 스크립트 로드 확인 메시지 (개발 모드에서만)
    if (window.dash_clientside && window.dash_clientside.no_update === undefined) {
        console.log('🔇 React lifecycle warnings suppressed for Dash 3.2.0');
    }
})();