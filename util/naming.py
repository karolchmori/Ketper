import re

def modifyName(action, itemName, value):
    modifiedValue = ""
    if action == 'prefix':
        modifiedValue = addPrefix(itemName,value)
    elif action == 'suffix':
        modifiedValue = addSuffix(itemName,value)
    elif action == 'delete':
        modifiedValue = replaceText(itemName, value, '')

    return modifiedValue


def modifyNameList(action, listItems, value, newValue):
    newList = []

    if listItems:
        for item in listItems:
            if action == 'prefix':
                newItem = addPrefix(item,value)
            elif action == 'suffix':
                newItem = addSuffix(item,value)
            elif action == 'replace':
                newItem = replaceText(item, value, newValue)

            #newItem = modifyName(action, item, value)
            newList.append(newItem)

        return newList

#region Pattern

def notNumber(text):
    pattern = r'\d'
    return not re.search(pattern, text)

def isTextNumber(text):
    validation = re.fullmatch(r'[a-zA-Z0-9_]+', text)
    return validation
#endregion

#notNumber('123A')

def addPrefix(text, addition):
    modifiedText = addition + text
    return modifiedText

def addSuffix(text, addition):
    modifiedText = text + addition
    return modifiedText

def replaceText(textOriginal, textOld, textNew):
    modifiedText = textOriginal.replace(textOld, textNew)
    return modifiedText

#print(replaceText('Hello_oldWorld','old','new'))


def fillNumber(number, fillchar, totalLen, side):
    if side == 'R':
        modifiedText = str(number).rjust(totalLen, fillchar)
    elif side == 'L':
        modifiedText = str(number).ljust(totalLen, fillchar)
    return modifiedText

#print(fillNumber(5,'*',4,'L'))

def generateLetterByNumber(arrayNumber):
    modifiedText = ''
    for number in arrayNumber:
        word = chr(65 + number - 1)
        modifiedText = modifiedText + word
    return modifiedText
#print(generateLetterByNumber([1, 2, 3]))

def generateArrayColumns(value, columnNumber):
    finalArray = []

    for i in range(columnNumber):
        finalArray.append(value)

    return finalArray

#enerateArrayColumns(1,5)

def getArrayColumnsByPosition(array, position, valueStart, valueLimit):

    for i in range(position - 1):
        array = getNextNumArray(array, valueStart, valueLimit)
        #print('Position: ', i )
        #print('Array: ', array)
    return array


#I only want to change it once, give an array,  give me back the next number
def getNextNumArray(array, valueStart, valueLimit):
    lastColumn = len(array) - 1
    limitBool = False

    for i in range(len(array)):
        currentColumn = lastColumn - i

        if array[currentColumn] + 1 > valueLimit: #If its bigger than the limit will change the left column
            #If the column exceeds the valueLimit, do nothing and check next column
            limitBool = True
            #print('Exceeds in column: ', currentColumn)
        else:
            array[currentColumn] = array[currentColumn] + 1

            if limitBool:
                for j in range(lastColumn - currentColumn):
                    j = lastColumn - j
                    array[j] = valueStart
                    #print("Will modify column: ", j)

            break
    return array




#I only want to change it once, give an array,  give me back the last number
def getLastNumArray(array, valueStart, valueLimit):
    lastColumn = len(array) - 1
    limitBool = False

    for i in range(len(array)):
        currentColumn = lastColumn - i

        if array[currentColumn] - 1 < valueLimit: #If its bigger than the limit will change the left column
            #If the column exceeds the valueLimit, do nothing and check next column
            limitBool = True
            #print('Exceeds in column: ', currentColumn)
        else:
            array[currentColumn] = array[currentColumn] - 1

            if limitBool:
                for j in range(lastColumn - currentColumn):
                    j = lastColumn - j
                    array[j] = valueStart
                    #print("Will modify column: ", j)

            break
    return array


#print(getLastNumArray([1, 1, 4, 1, 1], 4, 1))
