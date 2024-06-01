// 獲取modal元素
const loginModal = document.getElementById("loginModal");
const registerModal = document.getElementById("registerModal");

// 獲取打開modal的按鈕
const loginBtn = document.getElementById("loginBtn");
const registerBtn = document.getElementById("registerBtn");

// 獲取關閉modal的按鈕
const closeButtons = document.getElementsByClassName("close");

// 打開modal
loginBtn.onclick = function () {
    loginModal.style.display = "block";
}

registerBtn.onclick = function () {
    registerModal.style.display = "block";
}

// 關閉modal
for (let i = 0; i < closeButtons.length; i++) {
    closeButtons[i].onclick = function () {
        loginModal.style.display = "none";
        registerModal.style.display = "none";
    }
}

// 當點擊modal外部時關閉modal
window.onclick = function (event) {
    if (event.target == loginModal) {
        loginModal.style.display = "none";
    } else if (event.target == registerModal) {
        registerModal.style.display = "none";
    }
}