package org.openapitools.repository;

import org.openapitools.model.Order;
import org.springframework.stereotype.Repository;

@Repository
public class OrderRepository extends HashMapRepository<Order, Long> {

    @Override
    <S extends Order> Long getEntityId(S order) {
        return order.getId();
    }
}
