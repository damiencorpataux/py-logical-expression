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

    def __repr__(self):
        #FIXME: return Dialect.property(property)
        return "{%s}" % self.__name

    def __eq__(self, value):
        return Operand(self, 'eq', value)

    def __ne__(self, value):
        return Operand(self, 'ne', value)

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
    def __repr__(self):
        if isinstance(self, Expression):
            if type(self) is Operand:
                left, operator, right = self.property, self.comparator, self.value
            if type(self) is Expression:
                left, operator, right = self.left, self.operator, self.right
            return "({0}<-{1}->{2})".format(repr(left), operator, repr(right))
        else:
            return "{0}(%s)".format(self.__class_.__name__,
                                    self)

class Dialect(Base):
    """
    Define serialization dialect.
    TODO: make a pluggable dialect design.
    """
    comparators = {'eq': 'eq',
                   'ne': 'ne',
                   'gt': 'gt',
                   'ge': 'ge',
                   'lt': 'lt',
                   'le': 'le'}

    operators = {'and': 'and',
                 'or': 'or'}

    values = {(True, type(True)): True,
              (False, type(False)): False,
              (None, type(None)): None}

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
        return cls.values.get((value, type(value)), value)

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
        def nest(operand):
            #print type(operand), operand
            if type(operand) is Operand:
                return "%s" % operand
            elif type(operand) is Expression:
                return ("(%s)" % operand)
            else:
                return operand
                raise ValueError('Operand should not be %s "%s"'
                                 % (type(operand), operand))
        left = nest(expression.left)
        right = nest(expression.right)
        if expression.right:
            e = "{left} {operator} {right}"
        else:
            e = "{left}"
        return e.format(left=left,
                        operator=cls.operators[expression.operator],
                        right=right)

class Expression(Base):
    left = None
    operator = None
    right = None

    def __init__(self, left, operator, right):
        # NOTE: - left and right can be an Operand or Expression object,
        #       - right can be None (in this case operator has no meaning)
        if not isinstance(left, (Operand, Expression)):
            raise TypeError('Right must be of type Operand or Expression, '
                            'was %s' % type(right))
        self.left = left
        self.operator = operator
        if not isinstance(right, (Operand, Expression, type(None))):
            raise TypeError('Left must be of type Operand, Expression or None, '
                            'was %s' % type(right))
        self.right = right

    def __and__(self, other):
        return Expression(self, 'and', other)

    def __or__(self, other):
        return Expression(self, 'or', other)

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
        operands = list(operands)
        right = operands.pop()
        for operand in reversed(operands):
            right = Expression(operand, operator, right)
        return right

class Operand(Expression):
    #FIXME: Operand could/should be not be coded. Expression suffice...
    #       Operand extends Expression to be able to .and_() and ._or()
    #       but this is non-sense, the Operand walks and talks like Expression,
    #       therefore it is an Expression.
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

def e(*operands):
    """
    Alias for and_().
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


if __name__ == '__main__':
    """
    Examples and tests (TODO).
    """
    # print factory_by(name='k', a=1, b=2, z=9)
    ex = e(P.first == 1)
    print ex
    ex = ex.and_(P.last == 'n').or_(P.tail == 'yes')
    print ex
    ex = or_(ex, P.opt == False, P.may == True, P.no == None)
    print ex
    #print e(P.a == 'a', P.b >= 'b', or_(P.x == 1, P.y == 2), or_(P.xxx == 1, P.yyy == 2))
    ex
