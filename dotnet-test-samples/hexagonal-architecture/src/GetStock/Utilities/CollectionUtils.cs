namespace GetStock.Utilities
{
    public static class CollectionUtils
    {
        public static KeyValuePair<TKey, TValue> ToPair<TKey, TValue>(TKey key, TValue value)
        {
            return new KeyValuePair<TKey, TValue>(key, value);
        }
    }
}
