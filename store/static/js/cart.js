console.log('this is from my data')
document.addEventListener("DOMContentLoaded", function() {
 
    
    console.log("DOM fully loaded and parsed");

    var updateBtns = document.getElementsByClassName('update-cart');

    Array.from(updateBtns).map(function(btn) {
        btn.addEventListener('click', function() {
            var productId = this.dataset.product;
            var action = this.dataset.action;
            console.log('productId:', productId, 'Action:', action);

        });
    });
});