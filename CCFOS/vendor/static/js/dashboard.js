function showContent(type) {
    let content = '';

    if (type === 'orders') {
        content = `<h3 class="text-primary">All Orders</h3>
                   <ul>
                     <li>Order 1: Food Item A</li>
                     <li>Order 2: Food Item B</li>
                     <li>Order 3: Food Item C</li>
                   </ul>`;
    } 
    else if (type === 'cancelled-orders') {
        content = `<h3 class="text-danger">Cancelled Orders</h3>
                   <ul>
                     <li>Order 5: Cancelled due to non-payment</li>
                     <li>Order 8: Cancelled by user</li>
                   </ul>`;
    } 
    else if (type === 'pending-orders') {
        content = `<h3 class="text-warning">Pending Orders</h3>
                   <ul>
                     <li>Order 7: Waiting for confirmation</li>
                     <li>Order 10: Payment pending</li>
                   </ul>`;
    }

    document.getElementById('lower-dashboard').innerHTML = content;
}
