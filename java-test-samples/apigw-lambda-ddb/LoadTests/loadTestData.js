'use strict';
var Faker = require('faker');

module.exports = {
  generateRandomTicketData,
};

function generateRandomTicketData(requestParams, ctx, ee, next) {
  ctx.vars["userId"] = Faker.name.firstName();
  ctx.vars["description"] = Faker.lorem.sentence();

  return next();
}
