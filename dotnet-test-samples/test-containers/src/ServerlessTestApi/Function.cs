using Amazon.Lambda.Core;
using Amazon.Lambda.Serialization.SystemTextJson;

[assembly: LambdaSerializer(typeof(DefaultLambdaJsonSerializer))]

namespace ServerlessTestApi;

using System;
using System.Text.Json;
using System.Threading.Tasks;

using Amazon.Lambda.Annotations;
using Amazon.Lambda.Annotations.APIGateway;
using Amazon.Lambda.Core;

using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;

using Core.DataAccess;
using Core.Models;
using Infrastructure;

public class Function
{
    private readonly IProductsDAO _dataAccess;
    private readonly IOptions<JsonSerializerOptions> _jsonOptions;
    private readonly ILogger<Function> _logger;

    public Function(
        IProductsDAO dataAccess,
        ILogger<Function> logger,
        IOptions<JsonSerializerOptions> jsonOptions)
    {
        _dataAccess = dataAccess;
        _logger = logger;
        _jsonOptions = jsonOptions;
    }

    [LambdaFunction]
    [HttpApi(
        LambdaHttpMethod.Get,
        "/{id}")]
    public async Task<IHttpResult> GetProduct(string id, ILambdaContext context)
    {
        ProductDTO product;

        using var cts = context.GetCancellationTokenSource();
        try
        {
            product = await this._dataAccess.GetProduct(
                id,
                cts.Token);
        }
        catch (OperationCanceledException e)
        {
            this._logger.LogError(
                e,
                "Retrieving product timed out");

            return HttpResults.ServiceUnavailable();
        }
        catch (Exception e)
        {
            this._logger.LogError(
                e,
                "Failure retrieving product");

            return HttpResults.InternalServerError();
        }

        if (product == null)
        {
            return HttpResults.NotFound("Product not found");
        }

        return HttpResults.Ok(
            JsonSerializer.Serialize(
                product,
                this._jsonOptions.Value));
    }

    [LambdaFunction]
    [HttpApi(
        LambdaHttpMethod.Get,
        "/")]
    public async Task<IHttpResult> GetProducts(ILambdaContext context)
    {
        ProductWrapper products;

        using var cts = context.GetCancellationTokenSource();
        try
        {
            products = await this._dataAccess.GetAllProducts(cts.Token);
        }
        catch (OperationCanceledException e)
        {
            this._logger.LogError(
                e,
                "Retrieving product timed out");

            return HttpResults.ServiceUnavailable();
        }
        catch (Exception e)
        {
            this._logger.LogError(
                e,
                "Failure retrieving product");

            return HttpResults.InternalServerError();
        }

        return HttpResults.Ok(
            JsonSerializer.Serialize(
                products,
                this._jsonOptions.Value));
    }


    [LambdaFunction]
    [HttpApi(
        LambdaHttpMethod.Post,
        "/{id}")]
    public async Task<IHttpResult> CreateProduct(
        string id,
        [FromBody] ProductDTO product,
        ILambdaContext context)
    {
        UpsertResult result;

        using var cts = context.GetCancellationTokenSource();
        try
        {
            if (product == null)
            {
                return HttpResults.BadRequest("Body is required");
            }
            
            if ((!string.IsNullOrEmpty(product.Id) && product.Id != id) )
            {
                return HttpResults.BadRequest("Product ID in the body does not match path parameter");
            }

            result = await this._dataAccess.PutProduct(
                new(
                    id,
                    product.Name,
                    product.Price),
                cts.Token);
        }
        catch (OperationCanceledException e)
        {
            this._logger.LogError(
                e,
                "Inserting or updating a product timed out");

            return HttpResults.ServiceUnavailable();
        }
        catch (Exception e)
        {
            context.Logger.LogLine($"Error creating product {e.Message} {e.StackTrace}");

            return HttpResults.InternalServerError();
        }

        return result == UpsertResult.Inserted ? HttpResults.Created( $"Created product with id {id}") : HttpResults.Ok($"Updated product with id {id}");
    }


    [LambdaFunction]
    [HttpApi(
        LambdaHttpMethod.Delete,
        "/{id}")]
    public async Task<IHttpResult> DeleteProduct(
        string id,
        ILambdaContext context)
    {

        using var cts = context.GetCancellationTokenSource();
        
        try
        {
            await this._dataAccess.DeleteProduct(id, cts.Token);
                
            return HttpResults.Ok($"Deleted product with id {id}");
        }
        catch (OperationCanceledException e)
        {
            this._logger.LogError(
                e,
                "Inserting or updating a product timed out");

            return HttpResults.ServiceUnavailable();
        }
        catch (Exception e)
        {
            context.Logger.LogLine($"Error creating product {e.Message} {e.StackTrace}");

            return HttpResults.InternalServerError();
        }
    }
}