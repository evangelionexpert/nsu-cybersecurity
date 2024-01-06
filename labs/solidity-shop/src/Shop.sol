// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

struct Product {
    string message;
}

struct ProductInformation {
    uint256 productId;
    string name;
    uint256 price;
}

contract Shop is Ownable {
    // Events.
    event NewProductAdded(uint256 indexed productId);
    event ProductBoughtSuccesfully(uint256 indexed productId);

    error IncorrectMoneyValue(uint256 supposed, uint256 actual);
    error NoProductWithSuchId(uint256 yourId);
    error ProductIdAlreadyExists(uint256 productId);


    // Fields.
    ProductInformation[] private priceList;
    Product[] private products;
    mapping(uint256 => uint256) private productIdToArrId;


    // Methods.
    constructor() Ownable(msg.sender) {
    }

    function addProduct(Product memory _product, ProductInformation memory _info) public onlyOwner {
        if (productIdToArrId[_info.productId] != 0) {
            revert ProductIdAlreadyExists(_info.productId);
        }
        
        productIdToArrId[_info.productId] = priceList.length + 1;
        priceList.push(_info);
        products.push(_product);

        emit NewProductAdded(_info.productId);
    }

    function getPriceList() public view returns (ProductInformation[] memory) {
        return priceList;
    }

    function buyProduct(uint256  _productId) public payable returns (Product memory) {
        uint256 arrayId = productIdToArrId[_productId];

        if (arrayId == 0) {
            revert NoProductWithSuchId(_productId);
        }

        arrayId--;

        if (msg.value != priceList[arrayId].price) {
            revert IncorrectMoneyValue(priceList[arrayId].price, msg.value);
        }

        emit ProductBoughtSuccesfully(_productId);
        return products[arrayId];
    }
}
