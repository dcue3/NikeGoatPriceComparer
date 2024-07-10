//Attempt at using stockx api to extract prices, not working


const StockXAPI = require('stockx-api');
const stockX = new StockXAPI();

const sku = process.argv[2];

(async () => {
    try {
        // Returns an array of products
        const productList = await stockX.newSearchProducts(sku);


        if (productList.length === 0) {
            console.log(JSON.stringify({ error: `No products found for SKU: ${sku}` }));
            return;
        }

        // Fetch variants and product details of the first product
        const product = await stockX.fetchProductDetails(productList[0]);

        const productArray = product.variants;

        // Collect product details into an array
        const productDetails = productArray.map(variant => ({
            size: variant.size,
            lowestAsk: variant.market.lowestAsk,
            highestBid: variant.market.highestBid
        }));

        // Output the product details as JSON
        console.log(JSON.stringify({ sku, productDetails }));
    } catch (e) {
        console.error(JSON.stringify({ error: e.message }));
    }
})();
