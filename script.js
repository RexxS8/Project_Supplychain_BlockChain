// JavaScript untuk memastikan scroll horizontal
document.addEventListener("DOMContentLoaded", function() {
    console.log("JavaScript is successfully linked!");

    const transactionDetails = document.querySelector(".stTransactionDetails");

    // Memastikan transaksi yang baru dimuat dapat dilihat dengan scroll horizontal
    if (transactionDetails) {
        transactionDetails.addEventListener("DOMSubtreeModified", function() {
            transactionDetails.scrollLeft = transactionDetails.scrollWidth;
        });
    }

    // Tambahan: Scroll ke kanan saat pengguna memilih opsi yang berbeda
    const selectBox = document.querySelector(".stSelectbox");
    if (selectBox) {
        selectBox.addEventListener("change", function() {
            transactionDetails.scrollLeft = transactionDetails.scrollWidth;
        });
    }
});
