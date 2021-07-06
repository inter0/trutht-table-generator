logic_operators = (r"\/", "/\\", "=>", "<=>")

def split_formel(formel):
    formel = remove_outer_brackets(formel)
    split_formel_arr = []
    arr = formel.split(" ")

    #smallest split formel is something like a /\ b
    #if the length is smaller then 3, then you dont have a left and right term and an operation between them
    if len(arr) < 3:
        return None
    
    if arr[0] != "(":
        #thats the easy case
        #just get the first atom, the operator after it and the rest is the right subterm
        split_formel_arr.append(arr[0])
        split_formel_arr.append(arr[1])
        split_formel_arr.append(my_join(arr[2:], " "))
    else:
        #find the end of the subterm which the brackets encloses, which is the left term
        bracket = 0
        end_index_of_subterm = 0
        for index, f in enumerate(arr):
            if f == "(":
                bracket += 1
            if f == ")":
                bracket -= 1
            if bracket == 0:
                end_index_of_subterm = index + 1
                break
        split_formel_arr.append(my_join(arr[0:end_index_of_subterm], " "))
        split_formel_arr.append(arr[end_index_of_subterm])
        split_formel_arr.append(my_join(arr[end_index_of_subterm + 1:], " "))

    split_formel_arr = list(map(remove_outer_brackets, split_formel_arr))
    
    return split_formel_arr

def remove_outer_brackets(formel):
    """
    |   remove the outermost brackets
    |   if the bracket at the first formel position (formel[0]) closes at the end of the formel (formel[-1])
    """
    bracket = 0
    end_index = 0

    while True:
        arr = formel.split(" ")
        for index, f in enumerate(arr):
            if f == "(":
                bracket += 1
            if f == ")":
                bracket -= 1
            if bracket == 0:
                end_index = index
                break

        if end_index == len(arr) - 1 and end_index != 0:
            formel = formel[2:len(formel) - 2]
        else:
            break
        
    return formel

def my_join(lst, item):
    """
    |   same as "".join(lst), just insert item between every lst element
    """
    result = [item] * (len(lst) * 2 - 1)
    result[0::2] = lst
    return "".join(result)

#TODO: verify_formel has errors, it states a formel is not valid if an operator like <=> has a subterm like ( a /\ b) before or after it 
def verify_formel(formel):
    arr = formel.split(" ")

    #verify brackets
    bracket = 0
    for f in arr:
        if f == "(":
                bracket += 1
        if f == ")":
            bracket -= 1
    if bracket != 0:
        return False

    #verify atoms and quantors
    #TODO: subterms before and after a logical operator return false
    for index, f in enumerate(arr):
        if f in logic_operators:
            if index == 0:
                return False
            if not (is_atom(arr[index - 1]) and is_atom(arr[index + 1])):
                return False
    return True
               
def is_atom(chr):
    atom = True
    if chr in logic_operators:
        atom = False
    if chr == "(" or chr == ")":
        atom = False
    return atom

def implies(a, b):
    a ^= 1
    return a | b

def equivalence(a, b):
    if a == b:
        return 1
    else:
        return 0

def negate(a):
    a ^= 1
    return a

def my_and(a, b):
    return a & b

def my_or(a, b):
    return a | b

class operationNode():
    def __init__(self, operation, function):
        self.operation = operation
        self.function = function
        self.left_child = None
        self.right_child = None
        self.up_to_date_value = False
        self.string = None
        self.value = 0

    def get_value(self):
        if not self.up_to_date_value:
            self.value = self.function(self.left_child.get_value(), self.right_child.get_value())
            self.up_to_date_value = True
        return self.value 

    def __str__(self):
        if self.string == None:
            self.string = f"( {str(self.left_child)} {self.operation} {self.right_child} )"
        return self.string

class atomNode():
    def __init__(self, name, value, negated):
        self.name = name
        self.value = value
        self.negated = negated
    
    def get_value(self):
        return self.value
    
    def __str__(self):
        return self.name

class tree():
    functions = [my_or, my_and, implies, equivalence, negate]
    atomNode_arr = []

    def __init__(self, formel):
        #if not verify_formel(formel):
        #   raise Exception("Formel is not a valid formel")
        self.formel = formel
        self.top_node = self.__generate_tree()
    
    #TODO: more testing would be good
    def __generate_tree(self):
        split_formel_arr = split_formel(self.formel)

        #if formel cant be split more, this is an atom
        if split_formel_arr == None:
            node = None
            atomNodes_names_arr = tree.__get_atom_names(with_negated=True, sort_arr=False)
            negated = True if self.formel[0] == "-" else False

            #check if atom already exists, if it does return already existing atom otherwise create new atomNode
            if self.formel in atomNodes_names_arr:
                index = atomNodes_names_arr.index(self.formel)
                node = tree.atomNode_arr[index]
            else:
                node = atomNode(self.formel, 0, negated)
                tree.atomNode_arr.append(node)
            
            return node

        #create new operationNode and recursively build tree
        #set childs of this operationNode
        node = operationNode(split_formel_arr[1], tree.functions[logic_operators.index(split_formel_arr[1])])
        node.left_child = tree(split_formel_arr[0]).top_node
        node.right_child = tree(split_formel_arr[2]).top_node

        return node

    #TODO: test this
    #I dont know if it would be better if it would be ok if I only submit the changed atoms
    def update_values(self, value_dict):
        atom_names_arr = tree.__get_atom_names(with_negated=False, sort_arr=True)
        
        #check if lengths match
        if len(value_dict) != len(atom_names_arr):
            raise Exception("Length of value dictionary is not equal to number of atoms")
        
        #check if every atom of the formel tree is in the new values dictionary
        for atom_name in atom_names_arr:
            if atom_name not in list(value_dict.keys()):
                raise Exception("Given dictionary contains atoms that are not in the formel tree")

        for atom_name, new_value in value_dict.items():
            node = tree.__get_atomNode_by_name(atom_name)
            node.value = new_value
        
        #TODO: def need to test this
        for negated_atom in [atom for atom in tree.atomNode_arr if atom.negated]:
            new_value = negate(value_dict[negated_atom.name[1:]])
            negated_atom.value = new_value

        #update operationNodes up_to_date_value to False
        tree.__update_operationNodes(self.top_node)

    def __get_atomNode_by_name(name):
        for node in tree.atomNode_arr:
            if node.name == name:
                return node
        return None

    #TODO: test this
    def __update_operationNodes(node):
        if isinstance(node, operationNode):
            node.up_to_date_value = False
            tree.__update_operationNodes(node.left_child)
            tree.__update_operationNodes(node.right_child)
        
    #TODO: test this
    def __get_atom_names(with_negated=True, sort_arr=False):
        atom_names_arr = [atom.name for atom in tree.atomNode_arr]

        if not with_negated:
            for atom in tree.atomNode_arr:
                if atom.negated:
                    atom_names_arr.remove(atom.name)
            
        return atom_names_arr if not sort_arr else sorted(atom_names_arr)
    
    #TODO: this will definitly fail
    def evaluate(self, node):
        if isinstance(node, atomNode):
            return {str(node): node.value}
        
        dict = {str(node): node.value}
        dict_of_left_child = self.evaluate(node.left_child)
        dict_of_right_child = self.evaluate(node.right_child)

        dict_of_left_child.update(dict_of_right_child)
        dict_of_left_child.update(dict)

        return dict_of_left_child
