"""
    Dialect module.
"""

class Base(object):
    """
    Define serialization dialect.
    """
    operators = {'&':  '&',
                 '|':  '|',
                 '==': '==',
                 '<>': '<>',
                 '>':  '>',
                 '>=': '>=',
                 '<':  '<',
                 '<=': '<='}

    values = {(True, type(True)): True,
              (False, type(False)): False,
              (None, type(None)): None}

    @classmethod
    def property(cls, property):
        """
        Serialize Property object.
        """
        return property.name

    @classmethod
    def value(cls, value):
        """
        Serialize property value.
        """
        return "'%s'" % cls.values.get((value, type(value)), value)

    @classmethod
    def expression(cls, expression):
        """
        Serialize Expression object.
        """
        return "{left} {operator} {right}".format(
            left = expression.left
                   if expression.left.__class__.__name__ in ('Property', 'Expression')
                   else cls.value(expression.left),
            operator = cls.operators[expression.operator],
            right = expression.right
                    if expression.left.__class__.__name__ in ('Property', 'Expression')
                    else cls.value(expression.right))


class Python(Base):
    @classmethod
    def property(cls, property):
        return "P.%s" % property.name

    @classmethod
    def expression(cls, expression):
        # NOTE: Can do eval(repr(P.a==1))
        #       yet why not use a dialect called 'python' that can do that
        return "({0} {1} {2})".format(expression.left, expression.operator, expression.right)


class OData(Base):
    operators = {'&':  'and',
                 '|':  'or',
                 '==': 'eq',
                 '<>': 'ne',
                 '>':  'gt',
                 '>=': 'ge',
                 '<':  'lt',
                 '<=': 'le'}

    values = {(True, type(True)): True,
              (False, type(False)): False,
              (None, type(None)): None}

    @classmethod
    def value(cls, value):
        return "'%s'" % super(OData, cls).value(value)

    @classmethod
    def expression(cls, expression):
        return "%s" % super(OData, cls).expression(expression)
