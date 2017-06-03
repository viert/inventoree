const Lower = "abcdefghijklmnopqrstuvwxyz"
const Upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
const Digits = "0123456789"

export const succ = str => {

    // Ruby String.succ implementation
    const getAlphabeth = sym => {
        if (Lower.indexOf(sym) >= 0) {
            return Lower
        }
        if (Upper.indexOf(sym) >= 0) {
            return Upper
        }
        if (Digits.indexOf(sym) >= 0) {
            return Digits
        }
        return null;
    }

    const symbolSucc = sym => {
        let alphabeth = getAlphabeth(sym)
        if (alphabeth === null) return { newSym: null, alphabeth: null, carry: null } 

        let i = alphabeth.indexOf(sym) + 1
        let carry = false

        if (i === alphabeth.length) {
            carry = true
            i = 0
        }
        return { newSym: alphabeth[i], alphabeth, carry }
    }

    if (str.length === 0) return str
    let symList = str.split("").reverse()

    let i = 0
    while (true) {
        let sym = symList[i]

        let { newSym, alphabeth, carry } = symbolSucc(sym)
        if (newSym === null) return ""
        
        symList[i] = newSym
        if (!carry) break
        
        i++
        if (symList.length === i) {
            if (alphabeth === Digits) {
                symList.push(alphabeth[1])
            } else {
                symList.push(alphabeth[0])
            }
            break
        }
    }

    return symList.reverse().join("")
}

export const sequence = function* (fr, to, exclude) {
    while (fr !== to && fr.length <= to.length) {
        yield fr
        fr = succ(fr)
    }
    if (fr === to && !exclude) {
        yield fr
    }
}

export const expandSinglePattern = function* (pattern) {
    let singleExpr = /([0-9a-zA-Z]+)-([0-9a-zA-Z]+)/
    if (pattern.startsWith("[") && pattern.endsWith("]"))
        pattern = pattern.slice(1, pattern.length-1)

    let tokens = pattern.split(",")
    for (var token of tokens) {
        let corners = singleExpr.exec(token)
        if (corners == null) {
            yield token
        } else {
            for (var item of sequence(corners[1], corners[2])) {
                yield item
            }
        }
    }
}

export const getBracesIndices = pattern => {
    let stack = Array()
    let indices = Array()
    let currentIndex = Array()
    pattern.split("").forEach( (sym, ind) => {
        if (sym === "[") {
            stack.push(true)
            currentIndex.push(ind)
        } else if (sym === "]") {
            let test = stack.pop()
            if (test === undefined) {
                // Closing brace without opening one
                return []
            }
            currentIndex.push(ind)
        }
        if (currentIndex.length === 2) {
            if (stack.length !== 0) {
                // Nested patterns are prohibited
                return []
            }
            indices.push(currentIndex)
            currentIndex = Array()
        }
    })
    if (stack.length > 0) {
        // Closing brace is absent
        return []
    }
    return indices
}

export const expandPattern = function* (pattern) {
    let indices = getBracesIndices(pattern)
    if (indices.length === 0) {
        yield pattern
        return
    }
    let fr = indices[0][0], to = indices[0][1]
    for (var token of expandSinglePattern(pattern.slice(fr+1, to))) {
        for (var result of expandPattern(pattern.slice(0, fr) + token + pattern.slice(to+1))) {
            yield result
        }
    }
}