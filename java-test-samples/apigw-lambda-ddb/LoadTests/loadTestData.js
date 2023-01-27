'use strict';
var Faker = require('faker');

module.exports = {
  generateRandomProductData,
};

function generateRandomProductData(requestParams, ctx, ee, next) {
  ctx.vars["userId"] = Faker.name.firstName();
  ctx.vars["description"] = Faker.lorem.sentence();

  return next();
}
