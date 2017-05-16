"""
Logical Expression Microframework (WIP).
"""

class PropertyType(type):
    """
    Property type is used to generate Property objets.
    """
    def __getattr__(self, name):
        return Property(name)

    def __setattr__(self, name):
        raise AttributeError('PropertyType is read-only') #FIXME: exception class

class Property(object):
    """
    Represent a named and comparable property.
    """
    __metaclass__ = PropertyType
    __name = None

    def __init__(self, name):
        if not name or not isinstance(name, basestring):
            raise ValueError('Property name must be string and cannot be empty')
        self.__name = name

    def __str__(self):
        #FIXME: return Dialect.property(property)
        return self.__name

    def __eq__(self, value):
        return Operand(self, 'eq', value)

    def __gt__(self, value):
        return Operand(self, 'gt', value)

    def __ge__(self, value):
        return Operand(self, 'ge', value)

    def __lt__(self, value):
        return Operand(self, 'lt', value)

    def __le__(self, value):
        return Operand(self, 'le', value)

P = Property


class Base(object):
    pass

class Dialect(Base):
    """
    Define serialization dialect.
    TODO: make a pluggable dialect design.
    """
    comparators = {'eq': 'eq',
                   'gt': 'gt',
                   'ge': 'ge',
                   'lt': 'lt',
                   'le': 'le'}

    operators = {'and': 'and',
                 'or': 'or'}

    values = {True: True,
              False: False,
              None: None}

    @classmethod
    def property(cls, property):
        """
        Serialize Property object.
        """
        #FIXME: AttributeError: type object 'property' has no attribute '_Dialect__name'
        return property.__name
        #FIXME: AttributeError: type object 'property' has no attribute '__name'
        return getattr(property, '__name')

    @classmethod
    def value(cls, value):
        """
        Serialize property value.
        """
        return cls.values.get(value, value)

    @classmethod
    def operand(cls, operand):
        """
        Serialize Operand object.
        """
        return "{0.property} {1} {2}".format(operand,
                                             cls.comparators[operand.comparator],
                                             cls.value(operand.value))

    @classmethod
    def expression(cls, expression):
        """
        Serialize Expression object.
        """
        if expression.right:
            return "{0.left} {1} {0.right}".format(expression,
                                                   cls.operators[expression.operator])
        else:
            return "{0.left}".format(expression)

class Operand(Base):
    property = None
    comparator = None
    value = None

    def __init__(self, property, comparator, value):
        if not isinstance(property, Property):
            raise TypeError('Property must be of type Property')
        self.property = property
        self.comparator = comparator
        self.value = value

    def __str__(self):
        return Dialect.operand(self)

class Expression(object):
    left = None
    operator = None
    right = None

    def __init__(self, left, operator, right):
        # NOTE: - left and right can be an Operand or Expression object,
        #       - right can be None (in this case operator has no meaning)
        if not isinstance(left, (Operand, Expression)):
            raise TypeError('Right must be of type Operand or Expression')
        self.left = left
        self.operator = operator
        if not isinstance(right, (Operand, Expression, type(None))):
            raise TypeError('Left must be of type Operand, Expression or None')
        self.right = right

    def __str__(self):
        return Dialect.expression(self)

    def add(self, operator, *operands):
        return self.__class__.factory(operator, self, *operands)

    def and_(self, *operands):
        """
        Add the given operands to the Expression using the OR operator.
        """
        return self.add('and', *operands)

    def or_(self, *operands):
        """
        Add the given operands to the Expression using the AND operator.
        """
        return self.add('or', *operands)

    @staticmethod
    def factory(operator, *operands):
        """
        Produce an Expression object from the given operands.
        """
        right = None
        for operand in reversed(operands):
            right = Expression(operand, operator, right)
        return right


def factory(*operands):
    """
    Produce an Expression object from the given operands.
    """
    return and_(*operands)

def and_(*operands):
    """
    Produce an Expression object with operands and AND operator.
    """
    return Expression.factory('and', *operands)

def or_(*operands):
    """
    Produce an Expression object with operands and the OR operator.
    """
    return Expression.factory('or', *operands)


# FIXME: could be merged with factory ?
# def factory_by(**kwargs):
#     """
#     Produce an Expression object from the given keyword arguments.
#     Note that the operands are not in order in the produced expression.
#     """
#     return factory(*[getattr(Property, k) == v for k, v in kwargs.viewitems()])


if __name__ == '__main__':
    """
    Examples and tests (TODO).
    """
    # print factory_by(name='k', a=1, b=2, z=9)
    print factory(P.a == 'a', P.b >= 'b', or_(P.x == 1, P.y == 2)) #FIXME: x and y must be nested in the generated expression
    e = factory(P.first == 1)
    print e
    e = e.and_(P.last == 'n').or_(P.tail == 'yes')
    print e
    e = or_(e, P.opt == False, P.may == True, P.no == None)
    print e
