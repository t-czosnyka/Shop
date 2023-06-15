<h1>MyShop</h1>

<p>My Django framework training project - e-commerce application for a clothing store.</p>
<p>See live on: https://eu.pythonanywhere.com/user/tczosnyka</p>

<h2>Description:</h2>
<p> Application allows different categories of products. Each category of product can have unique attributes.
One product can also have different variants e.g. color, size. The user can select a product feature, like color, 
and the application will dynamically filter available product variants with this feature. When all features
are selected product may be added to the cart and then ordered.</p>
<p>User accounts are implemented. Logged-in user can rate and comment on products, view past orders and have order data
filled in automatically. Accounts must be confirmed by activation link sent on provided email address. Password reset
is possible by email.</p>
<p>Orders can be placed without logging in. In this case order confirmation by email is required. 
When order is confirmed payment through Stripe API is possible. Payment link is also send to user email address.</p>

<p> While the frontend is not the primary focus of this project, Bootstrap 5 and some basic JS
is used to make it look nicer.</p>

<p>By design only function based views are used in this project.</p>

<h3>Features:</h3>
<ul>
  <li>Different product categories with flexible parameters,</li>
  <li>Different product variants with dynamic querying,</li>
  <li>Shopping cart,</li>
  <li>Product images with ability to set main image,</li>
  <li>User accounts management - registration, logging in, logging out, account activation by email, 
                              password reset by email,</li>
  <li>Order processing - with or without(email confirmation required) logging in,</li>
  <li>Comments and ratings for products,</li>
  <li>Product category pages,</li>
  <li>Comments and products ordering and filtering,</li>
  <li>Payment processing with Stripe API.</li>
</ul>

<h2>Screenshots:</h2>

<p>Home page:</p>
<img src="https://github.com/t-czosnyka/Shop/assets/115980948/3f3dacd0-8db3-4c84-9a21-27e4510219df" style="height:500px">
</br></br>

<p>Shopping cart:</p>
<img src="https://github.com/t-czosnyka/Shop/assets/115980948/b96bbe93-f4c1-42ff-8f96-faefc79dcfa2" style="height:300px">
</br></br>

<p>Product detail:</p>
<img src="https://github.com/t-czosnyka/Shop/assets/115980948/4f66ce1c-8fb9-415f-b01c-73f0d68f5831" style="height:500px">
</br></br>

<p>Product category:</p>
<img src="https://github.com/t-czosnyka/Shop/assets/115980948/9879730e-420c-4f83-8628-f3af452fa502" style="height:400px">
</br></br>

<p>User registation:</p>
<img src="https://github.com/t-czosnyka/Shop/assets/115980948/2881c782-14a3-44b3-9071-deb3f28556ce" style="height:400px">
</br></br>

<p>User menu:</p>
<img src="https://github.com/t-czosnyka/Shop/assets/115980948/52c63847-95e2-4128-994a-d5438c449137" style="height:200px">
</br></br>

<p>User comments:</p>
<img src="https://github.com/t-czosnyka/Shop/assets/115980948/45bf8c17-f013-4a80-a9da-c244e5f423c1" style="height:400px">
</br></br>

<p>Orders list:</p>
<img src="https://github.com/t-czosnyka/Shop/assets/115980948/2df95084-bc70-4ee5-85c6-8b1737a035f8" style="height:400px">
</br></br>

<p>Order detail:</p>
<img src="https://github.com/t-czosnyka/Shop/assets/115980948/d37384ab-6352-4bfe-8e39-6e32cd953c86" style="height:400px">
</br></br>

<p>Stripe payment:</p>
<img src="https://github.com/t-czosnyka/Shop/assets/115980948/24ad5071-7493-4955-81e8-f58d277547c9" style="height:300px">
</br></br>




