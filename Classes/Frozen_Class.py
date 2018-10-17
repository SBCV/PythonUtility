# https://stackoverflow.com/questions/16017397/injecting-function-call-after-init-with-decorator
# define a new metaclass which overrides the "__call__" function
class InitModifier(type):
    def __call__(cls, *args, **kwargs):
        """Called when you call MyNewClass() """
        obj = type.__call__(cls, *args, **kwargs)

        # Each time init() is called, so is freeze()
        obj._freeze()

        return obj


# https://stackoverflow.com/questions/3603502/prevent-creating-new-attributes-outside-init
class FrozenClassTemplate(object):
    __isfrozen = False
    def __setattr__(self, key, value):
        if self.__isfrozen and not hasattr(self, key):
            raise TypeError(
                "\"" + self.__class__.__name__  + "\" is a frozen class. "
                "Adding of attributes after init() is forbidden. "
                "Attribute \"" + str(key) + "\" is not defined. "
                "Did you misspelled the attribute?"
                )
        object.__setattr__(self, key, value)

    def _freeze(self):
        self.__isfrozen = True


class FrozenClass(FrozenClassTemplate):
    # Note: named tuples are immutable, -> can't use them for this purpose
    __metaclass__ = InitModifier
