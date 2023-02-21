namespace ApiTests.IntegrationTest.Drivers
{
    public class ProductWrapper
    {
        public ProductWrapper(List<Product> products) => Products = products;

        public List<Product> Products { get; }
    }
}