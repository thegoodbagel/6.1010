(begin
  (define (map func lst) 
        (if (equal? (length lst) 0) 
            lst 
            (cons (func (car lst)) (map func (cdr lst)))
        )
    )
  (define (filter func lst) 
        (if (equal? (length lst) 0) 
            lst 
            (if (equal? (func (car lst)) #t) 
                (cons (car lst) (filter func (cdr lst)))
                (filter func (cdr lst))
            )
        )
    )
  (define (reduce func lst initval)
        (if (equal? (length lst) 0) 
            initval 
            (reduce 
                func (cdr lst) (func initval (car lst))
            )
        )
    )
)