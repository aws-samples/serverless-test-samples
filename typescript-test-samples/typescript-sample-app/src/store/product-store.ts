// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0
import { AnyProduct } from "../model/product";

export interface ProductStore {
  getProduct: (id: string) => Promise<AnyProduct | undefined>;
  putProduct: (product: AnyProduct) => Promise<void>;
  deleteProduct: (id: string) => Promise<void>;
  getProducts: () => Promise<AnyProduct[] | undefined>;
}
